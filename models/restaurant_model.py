import random
from statistics import fmean

import math
from mesa import Model
from mesa.space import SingleGrid

from agents.customer_agent import CustomerAgent
from agents.manager_agent import ManagerAgent
from agents.research_agent import ResearchAgent
from agents.route_agent import RouteAgent
from agents.service_agent import ServiceAgent
from data_structures.config.config import Config
from data_structures.config.logging_config import restaurant_logger
from data_structures.menu import Menu
from enums.customer_agent_state import CustomerAgentState
from main import history
from ml.lstm_model import LSTMModel

logger = restaurant_logger


class RestaurantModel(Model):
    """A model with some number of agents."""

    def __init__(self, lstm_model: LSTMModel):
        # Initialize the model and its properties
        super().__init__()

        # Initialize the LSTM model for time series prediction
        self.lstm_model = lstm_model

        # Initialize the menu of the restaurant including all available dishes
        self.menu = Menu()

        # Initialize the grid to visualize the restaurant layout
        self.grid = SingleGrid(Config().restaurant.grid_width, Config().restaurant.grid_height, False)

        # Initialize route lists that the service agents take to serve/seat customers
        self.serve_route: list[CustomerAgent] = []
        self.seat_route: list[CustomerAgent] = []

        # Initialize agents
        CustomerAgent.create_agents(
            model=self,
            n=Config().customers.max_new_customer_agents_per_step
        )
        RouteAgent.create_agents(
            model=self,
            n=1
        )
        # Note: ServiceAgents get employed by ManagerAgent
        ManagerAgent.create_agents(
            model=self,
            n=1
        )
        ResearchAgent.create_agents(
            model=self,
            n=1
        )

        logger.info(
            "Created model with %d customer agents, %d service agents and 1 manager agent",
            Config().customers.max_new_customer_agents_per_step,
            Config().service.service_agents
        )

    def step(self):
        """Advance the model by one step."""
        # Spawn new customers
        self.spawn_customers()

        # Step through all agents
        self.__step_through_agents()

        # Update the time series prediction model (online training) based on the 'real' data of the former step
        satisfaction_rating = (history.rating_history[self.steps - 1] if len(history.rating_history) > 1
                               else Config().rating.rating_default)
        self.lstm_model.update(
            last_step=self.steps - 1,
            customer_count=history.customers_added_history[self.steps - 1],
            satisfaction_rating=satisfaction_rating
        )

        # Step through the research agent to evaluate the model
        if ResearchAgent in self.agents_by_type.keys():
            research_agent = self.agents_by_type[ResearchAgent][0]
            research_agent.step()

        # Log the results of the current step
        total_time_spent = history.total_time_spent_history[-1]
        time_spent_change = (total_time_spent - (history.total_time_spent_history[self.steps - 2]
                                                 if len(history.total_time_spent_history) > 1 else 0))
        profit = history.profit_history[self.steps - 1] if len(history.profit_history) > 1 else 0

        log_message = f"Step {self.steps}: Evaluating model. Total time spent: {total_time_spent} (change: {time_spent_change}), profit: {profit}"
        logger.info(log_message)
        print(log_message)

    def spawn_customers(self):
        """
        Spawn a new customer agent based on an ML detectable pattern.
        
        The number of new customers is computed by combining several factors:
            - The current restaurant rating (total_rating_in_percent) is used as a baseline.
            - A periodic factor via a sine function simulates rush hours (e.g., a surge around lunchtime or dinner) and off-peak times.
            - The historical average of customers spawned (from customers_added_per_step_timeseries) is used for smoothing sudden changes.
            - A small random variation (±10% of the smoothed estimate) simulates unpredictable fluctuations.
            - The calculated number is then clamped so that both max_new_customer_agents_per_step and max capacity of customer agents in the restaurant (grid width * height) are not exceeded.
        """
        # Get the current restaurant rating.
        total_rating_in_percent: float = self.get_total_rating_percentage()  # e.g., 0.85 for 85%

        # Retrieve configuration limits.
        max_new_customers: int = Config().customers.max_new_customer_agents_per_step
        max_simultaneous_customers: int = Config().restaurant.grid_width * Config().restaurant.grid_height

        # Count current active customers (not DONE).
        current_customers: int = sum(
            1 for agent in self.agents_by_type[CustomerAgent]
            if agent.state != CustomerAgentState.DONE
        )

        # 1. Calculate baseline spawn count based solely on the current satisfaction rating.
        # A higher rating leads to a larger baseline number relative to the maximum allowed.
        baseline_spawn = total_rating_in_percent * max_new_customers

        # 2. Compute a periodic multiplier to simulate peak and off-peak periods.
        # Here, we define a cycle (e.g., one day) using a period of 100 steps.
        # The sine function produces a value between -1 and 1; scaling the result gives a multiplier
        # that boosts the spawn rate during "rush" periods and decreases it during quieter times.
        period_multiplier = 1 + 0.5 * math.sin(2 * math.pi * (self.steps / Config().run.full_day_cycle_period))

        # 3. Calculate the historical average of customers spawned from previous steps.
        # If no history exists, use half of the maximum as a default.
        if history.customers_added_history:
            historical_avg = sum(history.customers_added_history) / len(history.customers_added_history)
        else:
            historical_avg = max_new_customers / 2

        # 4. Smooth the instantaneous estimate by averaging the baseline with the historical average.
        smoothed_estimate = (baseline_spawn + historical_avg) / 2

        # 5. Combine the smoothed estimate with the periodic multiplier for time-based fluctuations.
        estimated_spawn = smoothed_estimate * period_multiplier

        # 6. Add minor random variation (up to ±10% of the smoothed estimate) for realism.
        random_variation = random.uniform(-0.1 * smoothed_estimate, 0.1 * smoothed_estimate)
        estimated_spawn += random_variation

        # 7. Clamp the estimated number so it does not exceed the maximum allowed for a step.
        amount = max(0, min(int(round(estimated_spawn)), max_new_customers))

        # 8. Ensure that spawning this many customers does not exceed the maximum allowed in the restaurant.
        available_slots = max_simultaneous_customers - current_customers
        if available_slots < amount:
            amount = max(0, available_slots)

        # 9. Finally, create the new customer agents.
        CustomerAgent.create_agents(model=self, n=amount)
        history.add_customers_added(amount)

        logger.info("Step %d: Spawned %d new customer agents. Current rating: %.2f (%.2f%%)",
                    self.steps, amount, self.get_total_rating(), self.get_total_rating_percentage() * 100)

    def get_total_rating_percentage(self) -> float:
        """
        Compute the total rating percentage for all customers in the model.
        :return: A value between 0 and 1, which represents the relative position of the overall rating within the possible rating range.
        """
        total_rating = ((self.get_total_rating() - Config().rating.rating_min) / (
                Config().rating.rating_max - Config().rating.rating_min))
        return total_rating

    def get_total_time_spent(self) -> int:
        """ Compute the total time spent for all customers in the model """
        return sum(agent.get_total_time() for agent in
                   self.agents_by_type[CustomerAgent])

    def get_waiting_time_spent(self) -> int:
        """ Compute the total time spent for all customers in the model """
        return sum(agent.waiting_time for agent in
                   self.agents_by_type[CustomerAgent])

    def get_total_rating(self) -> float | None:
        """ Compute the total rating for all customers in the model """
        return fmean(agent.rating for agent in self.agents_by_type[CustomerAgent]
                     if agent.rating is not None)

    def __step_through_agents(self):
        """Step through all agents in the model."""
        # If this is the first step, step the ManagerAgent first to handle shifts
        if self.steps == 1 and ManagerAgent in self.agents_by_type.keys():
            for agent in self.agents_by_type[ManagerAgent]:
                agent.step()

        # Step all agents manually, because Manager is scaling the ServiceAgents
        if CustomerAgent in self.agents_by_type.keys():
            for agent in self.agents_by_type[CustomerAgent]:
                agent.step()
        if ServiceAgent in self.agents_by_type.keys() and RouteAgent in self.agents_by_type.keys():
            # Step through the RouteAgent first to update the routes that the service agents take to serve/seat customers
            self.agents_by_type[RouteAgent][0].step()

            # Step through all ServiceAgents
            for agent in self.agents_by_type[ServiceAgent]:
                agent.step()
        if ManagerAgent in self.agents_by_type.keys() and self.steps > 1:
            for agent in self.agents_by_type[ManagerAgent]:
                agent.step()

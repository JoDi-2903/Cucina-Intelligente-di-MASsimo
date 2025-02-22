import math
import random
from statistics import fmean

from mesa import Model
from mesa.space import SingleGrid

from agents.customer_agent import CustomerAgent
from agents.manager_agent import ManagerAgent
from agents.service_agent import ServiceAgent
from enums.customer_agent_state import CustomerAgentState
from main import history
from ml.lstm_model import LSTMModel
from models.config.config import Config
from models.config.logging_config import restaurant_logger
from models.menu import Menu

logger = restaurant_logger


class RestaurantModel(Model):
    """A model with some number of agents."""

    def __init__(self, lstm_model: LSTMModel):
        super().__init__()

        # Initialize LSTM model, menu and history
        self.lstm_model = lstm_model
        self.menu = Menu()

        # Initialize agents
        CustomerAgent.create_agents(
            model=self,
            n=Config().customers.max_new_customer_agents_per_step
        )
        # Note: ServiceAgents get employed by ManagerAgent
        ManagerAgent.create_agents(
            model=self,
            n=1
        )

        # Initialize grid that visualizes the restaurant
        self.grid = SingleGrid(
            6,
            7,
            torus=False
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

        # Step all agents manually, because Manager is scaling the ServiceAgents
        if CustomerAgent in self.agents_by_type.keys():
            for agent in self.agents_by_type[CustomerAgent]:
                agent.step()
        if ServiceAgent in self.agents_by_type.keys():
            for agent in self.agents_by_type[ServiceAgent]:
                agent.step()
        if ManagerAgent in self.agents_by_type.keys():
            for agent in self.agents_by_type[ManagerAgent]:
                agent.step()

        # Update the time series prediction model (online training) based on the 'real' data of the former step
        satisfaction_rating = (history.rating_history[self.steps - 1] if len(history.rating_history) > 1
                               else Config().rating.rating_default)
        self.lstm_model.update(
            last_step=self.steps - 1,
            customer_count=history.customers_added_history[self.steps - 1],
            satisfaction_rating=satisfaction_rating
        )

        # Update the history data for visualization
        self.__update_histories()

        # Log the results of the current step
        total_time_spent = history.total_time_spent_history[-1]
        time_spent_change = (total_time_spent - (history.total_time_spent_history[self.steps - 2]
                                                 if len(history.total_time_spent_history) > 1 else 0))
        profit = history.profit_history[self.steps - 1]
        log_message = f"Step {self.steps}: Evaluating model. Total time spent: {total_time_spent} (change: {time_spent_change}), profit: {profit}"
        logger.info(log_message)
        print(log_message)

    def spawn_customers(self):
        """
        Spawn a new customer agent based on a ML detectable pattern.
        
        The number of new customers is computed by combining several factors:
            - The current restaurant rating (total_rating_in_percent) is used as a baseline.
            - A periodic factor via a sine function simulates rush hours (e.g., a surge around lunchtime or dinner) and off-peak times.
            - The historical average of customers spawned (from customers_added_per_step_timeseries) is used for smoothing sudden changes.
            - A small random variation (±10% of the smoothed estimate) simulates unpredictable fluctuations.
            - The calculated number is then clamped so that both max_new_customer_agents_per_step and max_simultaneous_customers_in_restaurant are not exceeded.
        """
        # Get the current restaurant rating.
        total_rating_in_percent: float = self.get_total_rating_percentage()  # e.g., 0.85 for 85%

        # Retrieve configuration limits.
        max_new_customers: int = Config().customers.max_new_customer_agents_per_step
        max_simultaneous_customers: int = Config().customers.max_simultaneous_customers_in_restaurant

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

    def __update_histories(self):
        """Update the history lists with the current values."""

        # Store the current step
        history.add_step(self.steps)

        # Evaluate the current rating of the restaurant
        history.add_rating(self.get_total_rating())

        # Calculate the total time that customers have spent in the restaurant waiting for their food
        history.add_total_time_spent(self.get_total_time_spent())
        history.add_total_waiting_time(self.get_waiting_time_spent())

        # Update the number of agents
        active_customer_agents = [  # Filter out all customers that are done
            agent for agent in self.agents_by_type[CustomerAgent]
            if agent.state != CustomerAgentState.DONE
        ]
        history.add_num_customer_agents(len(active_customer_agents))
        history.add_num_service_agents(len(self.agents_by_type[ServiceAgent]))
        history.add_num_manager_agents(len(self.agents_by_type[ManagerAgent]))
        history.add_num_agents(
            history.num_customer_agents_history[-1] +
            history.num_service_agents_history[-1] +
            history.num_manager_agents_history[-1]
        )

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

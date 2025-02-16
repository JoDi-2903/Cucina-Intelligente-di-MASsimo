import math
import random
from statistics import fmean

from mesa import Model

from enums.customer_agent_state import CustomerAgentState
from agents.customer_agent import CustomerAgent
from agents.manager_agent import ManagerAgent
from agents.service_agent import ServiceAgent
from ml.lstm_model import LSTMModel
from models.config.config import Config
from models.config.logging_config import restaurant_logger
from models.menu import Menu

logger = restaurant_logger

class RestaurantModel(Model):
    """A model with some number of agents."""

    # Store overall rating and number of created CustomerAgents per step over time
    rating_over_steps: dict[int, float] = {}
    customers_added_per_step: dict[int, int] = {}

    def __init__(self):
        super().__init__()

        # Create the menu
        self.menu = Menu()

        # Initialize agents
        CustomerAgent.create_agents(
            model=self,
            n=Config().customers.max_new_customer_agents_per_step
        )

        ServiceAgent.create_agents(
            model=self,
            n=Config().service.service_agents
        )

        ManagerAgent.create_agents(
            model=self,
            n=1
        )

        self.rating_over_steps[self.steps] = Config().rating.rating_default
        self.customers_added_per_step[self.steps] = Config().customers.max_new_customer_agents_per_step
        logger.info(f"Created model with {Config().customers.max_new_customer_agents_per_step} customer agents, {Config().service.service_agents} service agents and 1 manager agent")


    def step(self):
        """Advance the model by one step."""
        # save global rating of current step to history
        self.rating_over_steps[self.steps] = self.get_total_rating()

        # spawn new customers
        self.spawn_customers()

        # step all agents
        self.agents.shuffle_do("step")

        # Update the time series prediction model (online training) based on the 'real' data of the former step
        self.lstm_model.update(last_step=self.steps-1, customer_count=self.customers_added_per_step[self.steps-1], satisfaction_rating=self.rating_over_steps[self.steps-1])


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

        # Retrieve the historical data for customers added per step.
        customers_history: dict[int, int] = self.customers_added_per_step

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
        if customers_history:
            historical_avg = sum(customers_history.values()) / len(customers_history)
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
        self.customers_added_per_step[self.steps] = amount

        logger.info(
            f"Step {self.steps}: Spawned {amount} new customer agents. "
            f"Current rating: {self.get_total_rating():.2f} ({self.get_total_rating_percentage():.2%})"
        )

    # TODO: calculate time only for active agents or for all agents?
    def get_total_waiting_time(self) -> int:
        """ Compute the total waiting time for all customers in the model """
        return sum(agent.get_waiting_time() for agent in \
                   self.agents_by_type[CustomerAgent] \
                   if agent.state != CustomerAgentState.REJECTED)

    def get_total_ideal_time(self) -> int:
        """ Compute the total ideal time for all customers in the model """
        return sum(agent.get_ideal_time() for agent in \
                   self.agents_by_type[CustomerAgent] \
                   if agent.state != CustomerAgentState.REJECTED)

    def get_total_rating(self) -> float | None:
        """ Compute the total rating for all customers in the model """
        return fmean(agent.rating for agent in \
                     self.agents_by_type[CustomerAgent] \
                     if agent.rating is not None)

    def get_total_rating_percentage(self) -> float:
        """
        Compute the total rating percentage for all customers in the model.

        Returns:
            A value between 0 and 1, which represents the relative position of the overall rating within the possible rating range.
        """
        total_rating = ((self.get_total_rating() - Config().rating.rating_min) / (Config().rating.rating_max - Config().rating.rating_min))
        return total_rating

    def evaluate(self) -> tuple[int, float]:
        """ Evaluate the model for PyOptInterface objective function """
        manager = self.agents_by_type[ManagerAgent][0]

        logger.info(f"Step {self.steps}: Evaluating model. Total waiting time: {self.get_total_waiting_time()}, profit: {manager.profit}")
        return self.get_total_waiting_time(), manager.profit

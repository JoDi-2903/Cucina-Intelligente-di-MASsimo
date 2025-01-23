import random
import configparser
from enum import Enum
import mesa

class CustomerAgentState(Enum):
    """State for the CustomerAgent class"""
    WAIT_FOR_SERVICE_AGENT = 0
    EATING = 1
    FINISHED_EATING = 2

    def __str__(self):
        return self.name

class CustomerAgent(mesa.Agent):
    """An agent that represents a table of customers"""
    def __init__(self, model: mesa.Model, config: configparser.ConfigParser):
        # Pass parameters to parent class
        super().__init__(model)

        # Get config from configfile
        self.config = config

        # Create random number of people (at least 1)
        self.num_people = random.randint(
            1,
            int(self.config["Customers"]["max_customers_per_agent"])
        )

        # Create random number for time left (in minutes)
        self.time_left = random.randint(
            int(self.config["Customers"]["time_min"]),
            int(self.config["Customers"]["time_max"])
        )
        self.init_time = self.time_left

        # Served food needs time to be eaten. Value is set by ServiceAgent after serving
        self.eating_time = 0

        # Default correctness of the order: 95%
        self.order_correctness = float(self.config["Orders"]["order_correctness"])

        # Default rating is initally 5/5
        self.rating = int(self.config["Rating"]["rating_default"])
        self.rating_min = int(self.config["Rating"]["rating_min"])
        self.rating_max = int(self.config["Rating"]["rating_max"])

        # Track agent's state
        self.state = CustomerAgentState.WAIT_FOR_SERVICE_AGENT

    def calculate_table_rating(self):
        """Function to calculate the table rating according to waiting time exceeding and a random factor"""
        # Weight for waiting time exceeding
        alpha = float(self.config["Weights"]["time_exceeding"])
        # Weight for order errors
        beta = float(self.config["Weights"]["order_error"])
        # Error rate
        error_rate = 1 - self.order_correctness

        # Apply penalty only if time_left is negative (time exceeded)
        waiting_penalty = abs(self.time_left) * alpha if self.time_left < 0 else 0

        # Calculate final rating (0-5)
        self.rating = max(self.rating_min, self.rating_max - waiting_penalty - beta * error_rate)

    def get_global_rating_contribution(self):
        """Return the contribution to the global restaurant rating"""
        return self.rating * self.num_people

    def step(self):
        # If table is eating, reduce the eating time. If eating has finished, set state accordingly
        time_per_tick = int(self.config["Ticks"]["time_per_tick"])
        if self.state == CustomerAgentState.EATING:
            if self.eating_time > time_per_tick:
                self.eating_time -= time_per_tick
            else:
                self.state = CustomerAgentState.FINISHED_EATING
                self.calculate_table_rating()

        # Always reduce time left by the set per tick
        self.time_left -= time_per_tick
        print(self)

    def __str__(self):
        return f"CustomerAgent {self.unique_id} with {self.num_people} people in state {self.state}. Time left: {self.time_left}. Current rating: {self.rating}"

import logging
import os
import random

from mesa import Agent, Model

from enums.customer_agent_state import CustomerAgentState
from models.config.config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler(os.path.join("log", "customer_agent.log"))  # Log to file
    ]
)


class CustomerAgent(Agent):
    """An agent that represents a table of customers"""

    def __init__(self, model: Model):
        # Pass parameters to parent class
        super().__init__(model)

        # Get global config from model
        menu = self.model.menu

        # Create random number of people (at least 1)
        self.num_people = random.randint(
            1,
            Config().customers.max_customers_per_agent
        )

        # Create random number for time left (in minutes)
        self.time_left = random.randint(
            Config().customers.time_min,
            Config().customers.time_max
        )
        self.init_time = self.time_left

        # Randomly select food from menu
        self.menu_item = menu["menu"][random.randint(0, len(menu["menu"]) - 1)]
        # Retrieve eating time for selected menu item
        self.eating_time = self.menu_item["eatingTime"]
        # Retrieve eating time for selected menu item. Time is updated by service agent
        self.food_preparation_time = self.menu_item["preparationTime"]

        # Attribute to save the time of food arrival. Value is set by service agent
        self.food_arrival_time = 0

        # Default correctness of the order
        self.order_correctness = Config().orders.order_correctness

        # Default rating
        self.rating = Config().rating.rating_default
        self.rating_min = Config().rating.rating_min
        self.rating_max = Config().rating.rating_max

        # Track agent's state
        self.state = CustomerAgentState.WAIT_FOR_SERVICE_AGENT
        # print(self)

    def calculate_table_rating(self):
        """Function to calculate the table rating according to waiting time exceeding and a random factor"""
        # Weight for waiting time exceeding
        alpha = Config().weights.time_exceeding
        # Weight for order errors
        beta = Config().weights.order_error

        ####### Order Correctness Penalty

        # Generate a random number to simulate order correctness based on the percentage
        random_error = random.random()  # Generates a float between 0 and 1
        error_rate = 1 - self.order_correctness  # Convert correctness percentage to error rate

        # If the random number exceeds the order correctness, consider the order wrong
        order_error_penalty = beta * error_rate if random_error > self.order_correctness else 0

        ####### Exceeding Time Penalty

        # Ratio proportional to overall time
        exceedance_ratio = self.init_time + abs(self.time_left) / self.init_time \
            if self.time_left < 0 else 0

        # Apply penalty only if time_left is negative (time exceeded)
        waiting_penalty = exceedance_ratio * alpha if self.time_left < 0 else 0

        ####### Rating Variability

        # Introduce additional variability to the final rating
        rating_variability = random.uniform(-0.5, 0.5) * self.num_people

        ####### Final Rating

        self.rating = round(
            max(
                self.rating_min,
                min(
                    self.rating_max,
                    self.rating_max - waiting_penalty - order_error_penalty + rating_variability
                )
            ), 2
        )
        logging.debug(
            f"num people {self.num_people}, alpha {alpha}, beta {beta}, random error {random_error}, exceedance ratio {exceedance_ratio}, waiting penalty {waiting_penalty}, order error penalty {order_error_penalty}, rating variabilty {rating_variability}")

    def get_global_rating_contribution(self):
        """Return the contribution to the global restaurant rating"""
        return self.rating * self.num_people

    def step(self):
        # If agent is done, don't do anything and don't decrease time_left
        if self.state == CustomerAgentState.DONE:
            return

        # If customer is rejected, set rating to the worst and set agent to done
        if self.state == CustomerAgentState.REJECTED:
            self.rating = self.rating_min
            # print(self)
            logging.info(self)
            self.state = CustomerAgentState.DONE
            return

        # If table is eating, reduce the eating time
        if self.state == CustomerAgentState.EATING:
            if self.eating_time > 1:
                self.eating_time -= 1
            # If eating has finished, set state accordingly and set agent to done
            else:
                self.state = CustomerAgentState.FINISHED_EATING
                self.calculate_table_rating()
                # print(self)
                logging.info(self)
                self.state = CustomerAgentState.DONE
                return

        # Always reduce time left by 1
        self.time_left -= 1
        # print(self)

    def get_waiting_time(self):
        """ Calculate waiting time of agent"""
        return self.init_time - self.food_arrival_time

    def __str__(self):
        return f"CustomerAgent {self.unique_id} with {self.num_people} people in state {self.state}. Time left: {self.time_left}. Current rating: {self.rating}. Selected menu item: {self.menu_item}"

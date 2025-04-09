import random

from mesa import Agent, Model

from data_structures.config.config import Config
from data_structures.config.logging_config import customer_logger
from data_structures.menu import Menu
from enums.customer_agent_state import CustomerAgentState

logger = customer_logger


class CustomerAgent(Agent):
    """An agent that represents a table of customers"""

    def __init__(self, model: Model):
        # Pass parameters to parent class
        super().__init__(model)

        # Get menu from model
        menu: Menu = self.model.menu

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
        self.dish = menu.dishes[random.randint(0, len(menu.dishes) - 1)]
        # Retrieve eating time for selected dish
        self.eating_time = self.dish.eating_time
        # Retrieve food preparation time for selected dish. Time is updated by service agent
        self.food_preparation_time = self.dish.preparation_time

        # Attribute to save the time of food arrival. Value is set by service agent
        self.waiting_time = 0

        # Default correctness of the order
        self.order_correctness = Config().orders.order_correctness

        # Default rating
        self.rating = Config().rating.rating_default
        self.rating_min = Config().rating.rating_min
        self.rating_max = Config().rating.rating_max

        # Track agent's state
        self.state = CustomerAgentState.WAIT_FOR_SERVICE_AGENT

        logger.info(self)

    @classmethod
    def create_agents(cls, model: Model, n: int, *args, **kwargs):
        new_agents = super().create_agents(model, n, *args, **kwargs)
        return new_agents

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
        rating_variability = random.uniform(-1, 1) * self.num_people

        ####### Final Rating

        self.rating = max(
            self.rating_min,
            min(
                self.rating_max,
                int(self.rating_max - waiting_penalty - order_error_penalty + rating_variability)
            )
        )
        logger.debug(
            f"Customer {self.unique_id} rating {self.rating}. num people {self.num_people}, alpha {alpha:.2f}, beta {beta:.2f}, random error {random_error:.2f}, exceedance ratio {exceedance_ratio:.2f}, waiting penalty {waiting_penalty:.2f}, order error penalty {order_error_penalty:.2f}, rating variabilty {rating_variability:.2f}")

    def get_global_rating_contribution(self):
        """Return the contribution to the global restaurant rating"""
        return self.rating * self.num_people

    def step(self):
        # If agent is done, don't do anything and don't decrease time_left
        if self.state == CustomerAgentState.DONE:
            return

        # If agent finished eating, don't do anything and don't decrease time_left
        if self.state == CustomerAgentState.FINISHED_EATING:
            self.state = CustomerAgentState.DONE
            self.__leave_restaurant()
            return

        # If customer is rejected, set rating to the worst and set agent to done
        if self.state == CustomerAgentState.REJECTED:
            self.rating = self.rating_min
            logger.info(self)
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
                logger.info(self)
                return

        # Always reduce time left by 1
        self.time_left -= 1

        # Reduce rating if time is exceeded
        if self.time_left < 0:
            self.rating = self.rating_min
        elif self.init_time - self.time_left > 10:
            self.rating = max(self.rating_min, self.rating - 0.05)

        # logger.debug(self)

    def get_total_time(self):
        """ Calculate the total time the customer has spent in the restaurant. Increases if the customer has not finished eating. If they leave, the time is fixed. """
        return self.init_time - self.time_left

    def get_ideal_time(self):
        """ Calculate ideal time for the customer. Consists of food preparation time plus the time that is needed for eating. This is the minimum time the customer could possibly spend in the restaurant. """
        return self.food_preparation_time + self.eating_time

    def __str__(self):
        return f"Step {self.model.steps}: Customer {self.unique_id} with {self.num_people} people in state {self.state}. Time left: {self.time_left}. Current rating: {self.rating:.2f}. Selected dish: {self.dish}"

    def __leave_restaurant(self):
        """Remove the customer from the restaurant's grid."""
        self.model.grid.remove_agent(self)

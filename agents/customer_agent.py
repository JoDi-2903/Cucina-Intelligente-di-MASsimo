import random
import logging
from enum import Enum
import mesa

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(), # Log to console
        logging.FileHandler("log/customer_agent.log") # Log to file
    ]
)

class CustomerAgentState(Enum):
    """State for the CustomerAgent class"""
    WAIT_FOR_SERVICE_AGENT = 0  # gets selected by ServiceAgent
    WAITING_FOR_FOOD = 1
    EATING = 2
    FINISHED_EATING = 3         # rating accordingly + agent removed from model
    REJECTED = 4                # worst rating + agent removed from model

    def __str__(self):
        return self.name

class CustomerAgent(mesa.Agent):
    """An agent that represents a table of customers"""
    def __init__(self, model: mesa.Model):
        # Pass parameters to parent class
        super().__init__(model)

        # Get global config from model
        config = self.model.config
        menu = self.model.menu

        # Create random number of people (at least 1)
        self.num_people = random.randint(
            1,
            int(config["Customers"]["max_customers_per_agent"])
        )

        # Create random number for time left (in minutes)
        self.time_left = random.randint(
            int(config["Customers"]["time_min"]),
            int(config["Customers"]["time_max"])
        )
        self.init_time = self.time_left

        # Randomly select food from menu
        self.menu_item = menu["menu"][random.randint(0, len(menu["menu"])-1)]
        # Retrieve eating time for selected menu item
        self.eating_time = self.menu_item["eatingTime"]
        # Retrieve eating time for selected menu item. Time is updated by service agent
        self.food_preparation_time = self.menu_item["preparationTime"]

        # Default correctness of the order
        self.order_correctness = float(config["Orders"]["order_correctness"])

        # Default rating
        self.rating = int(config["Rating"]["rating_default"])
        self.rating_min = int(config["Rating"]["rating_min"])
        self.rating_max = int(config["Rating"]["rating_max"])

        # Track agent's state
        self.state = CustomerAgentState.WAIT_FOR_SERVICE_AGENT
        # print(self)

    def calculate_table_rating(self):
        """Function to calculate the table rating according to waiting time exceeding and a random factor"""
        # Weight for waiting time exceeding
        alpha = float(self.model.config["Weights"]["time_exceeding"])
        # Weight for order errors
        beta = float(self.model.config["Weights"]["order_error"])


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
        logging.debug(f"num people {self.num_people}, alpha {alpha}, beta {beta}, random error {random_error}, exceedance ratio {exceedance_ratio}, waiting penalty {waiting_penalty}, order error penalty {order_error_penalty}, rating variabilty {rating_variability}")

    def get_global_rating_contribution(self):
        """Return the contribution to the global restaurant rating"""
        return self.rating * self.num_people

    def step(self):
        # If customer is rejected, set rating to the worst and remove agent from model
        if self.state == CustomerAgentState.REJECTED:
            self.rating = self.rating_min
            # print(self)
            logging.info(self)
            self.remove()
            return

        # If table is eating, reduce the eating time
        if self.state == CustomerAgentState.EATING:
            if self.eating_time > 1:
                self.eating_time -= 1
            # If eating has finished, set state accordingly and remove agent from model
            else:
                self.state = CustomerAgentState.FINISHED_EATING
                self.calculate_table_rating()
                # print(self)
                logging.info(self)
                self.remove()
                return

        # Always reduce time left by 1
        self.time_left -= 1
        # print(self)

    def __str__(self):
        return f"CustomerAgent {self.unique_id} with {self.num_people} people in state {self.state}. Time left: {self.time_left}. Current rating: {self.rating}. Selected menu item: {self.menu_item}"

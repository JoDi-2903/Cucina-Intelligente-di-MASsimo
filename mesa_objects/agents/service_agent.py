import math
import random

from mesa import Agent, Model

from enums.customer_agent_state import CustomerAgentState
from mesa_objects.agents import customer_agent
from models.config.config import Config


class ServiceAgent(Agent):
    """An agent that represents the service in the restaurant"""

    def __init__(self, model: Model):
        super().__init__(model)

        # Initialize the queue for customers. Queue is limited by capacity
        self.customer_queue: list[customer_agent.CustomerAgent] = []

    def step(self):
        # Remove all customers that are done eating
        for c in self.customer_queue:
            if c.state == CustomerAgentState.DONE:
                self.customer_queue.remove(c)

        # Filter and sort new customers by time_left
        waiting_customers = sorted(
            (a for a in self.model.agents_by_type[customer_agent.CustomerAgent]
             if a.state == CustomerAgentState.WAIT_FOR_SERVICE_AGENT),
            key=lambda c: c.time_left
        )

        # Get the customer with the smallest time_left
        if waiting_customers:
            customer = waiting_customers[0]

            # Check if the customer needs to be rejected
            if customer.menu_item["preparationTime"] + customer.menu_item["eatingTime"] \
                    > customer.time_left:
                customer.state = CustomerAgentState.REJECTED

            # Check if the personal queue is full
            elif len(self.customer_queue) < Config().service.service_agent_capacity:
                # Add the customer to the queue and update their state
                self.customer_queue.append(customer)
                customer.state = CustomerAgentState.WAITING_FOR_FOOD

        # Filter and sort customers waiting for food
        waiting_customers = sorted(
            (a for a in self.model.agents_by_type[customer_agent.CustomerAgent]
             if a.state == CustomerAgentState.WAITING_FOR_FOOD),
            key=lambda c: c.time_left
        )

        # Get the customer with the smallest time_left
        if waiting_customers:
            customer = waiting_customers[0]

            # Only the specified amount of food can be processed at once.
            # The delay depends on the amount of customers
            preparation_delay = math.ceil(
                customer.num_people / Config().orders.parallel_preparation
            )

            # Occasionally introduce a probabilistic delay based on order_correctness
            random_delay = random.randint(0, Config().orders.delay_max) \
                if random.random() > Config().orders.delay_randomness \
                else 0

            # Total delay combines the batch adjustment and random delay (if applicable)
            total_delay = preparation_delay + random_delay

            # Prepare the food
            if customer.food_preparation_time > 1 + total_delay:
                customer.food_preparation_time -= 1
            else:
                customer.state = CustomerAgentState.EATING
                customer.food_arrival_time = customer.time_left

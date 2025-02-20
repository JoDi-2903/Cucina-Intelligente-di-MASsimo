import random

import math
from mesa import Agent, Model

from enums.customer_agent_state import CustomerAgentState
from agents.customer_agent import CustomerAgent
from models.config.config import Config
from models.config.logging_config import service_logger

logger = service_logger

class ServiceAgent(Agent):
    """An agent that represents the service in the restaurant"""

    def __init__(self, model: Model):
        super().__init__(model)

        # Initialize the queue for customers. Queue is limited by capacity
        self.customer_queue: list[CustomerAgent] = []

    def weighted_sort(self, customer: CustomerAgent):
        """ Custom sort key for sorting customers by weighted criteria """
        return sum(
            (customer.dish.profit * customer.num_people) * Config().weights.rating_profit,
            customer.get_waiting_time() * Config().weights.rating_waiting_time,
            customer.time_left * Config().weights.rating_total_time
        )

    def step(self):
        # Remove all customers that are done eating
        for c in self.customer_queue:
            if c.state == CustomerAgentState.DONE:
                self.customer_queue.remove(c)

        # Filter and sort new customers by weighted sort
        waiting_customers = sorted(
            (a for a in self.model.agents_by_type[CustomerAgent]
             if a.state == CustomerAgentState.WAIT_FOR_SERVICE_AGENT),
            key=self.weighted_sort
        )

        # Get the customer with the smallest time_left
        if waiting_customers:
            customer: CustomerAgent = waiting_customers[0]

            # Check if the customer needs to be rejected
            if customer.dish.preparation_time + customer.dish.eating_time \
                    > customer.time_left:
                customer.state = CustomerAgentState.REJECTED

            # Check if the personal queue is full
            elif len(self.customer_queue) < Config().service.service_agent_capacity:
                # Add the customer to the queue and update their state
                self.customer_queue.append(customer)
                customer.state = CustomerAgentState.WAITING_FOR_FOOD

            logger.info(f"Step {self.model.steps}: Service agent {self.unique_id} is serving customer {customer.unique_id}. Customer is currently {customer.state}")

        # Filter and sort customers waiting for food by weighted sort
        # TODO JK: update weighted sort to also consider the food preparation time
        waiting_customers = sorted(
            (a for a in self.customer_queue if a.state == CustomerAgentState.WAITING_FOR_FOOD),
            key=self.weighted_sort
        )

        # Get the customer with the smallest time_left
        if waiting_customers:
            customer: CustomerAgent = waiting_customers[0]

            # # Only the specified amount of food can be processed at once.
            # # The delay depends on the amount of customers
            # preparation_delay = math.ceil(
            #     customer.num_people / Config().orders.parallel_preparation
            # )

            # # Occasionally introduce a probabilistic delay based on order_correctness
            # random_delay = random.randint(0, Config().orders.delay_max) \
            #     if random.random() > Config().orders.delay_randomness \
            #     else 0

            # # Total delay combines the batch adjustment and random delay (if applicable)
            # total_delay = preparation_delay + random_delay

            # Prepare the food
            if customer.food_preparation_time > 1:
                customer.food_preparation_time -= 1
            else:
                customer.state = CustomerAgentState.EATING
                customer.food_arrival_time = customer.time_left

            logger.info(f"Step {self.model.steps}: Service agent {self.unique_id} is serving customer {customer.unique_id}. Customer is currently {customer.state}.")

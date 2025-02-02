from agents import customer_agent
import random
import math
import mesa

class ServiceAgent(mesa.Agent):
    """An agent that represents the service in the restaurant"""
    def __init__(self, model: mesa.Model):
        super().__init__(model)

        # Initialize the queue for customers. Queue is limited by capacity
        self.customer_queue: list[customer_agent.CustomerAgent] = []

    def step(self):
        # Remove all customers that are done eating
        for c in self.customer_queue:
            if c.state == customer_agent.CustomerAgentState.DONE:
                self.customer_queue.remove(c)

        # Filter and sort new customers by time_left
        waiting_customers = sorted(
            (a for a in self.model.agents_by_type[customer_agent.CustomerAgent]
             if a.state == customer_agent.CustomerAgentState.WAIT_FOR_SERVICE_AGENT),
            key=lambda c: c.time_left
        )

        # Get the customer with the smallest time_left
        if waiting_customers:
            customer = waiting_customers[0]

            # Check if the customer needs to be rejected
            if customer.menu_item["preparationTime"] + customer.menu_item["eatingTime"] \
                > customer.time_left:
                customer.state = customer_agent.CustomerAgentState.REJECTED

            # Check if the personal queue is full
            elif len(self.customer_queue) < int(self.model.config["Service"]["service_agent_capacity"]):
                # Add the customer to the queue and update their state
                self.customer_queue.append(customer)
                customer.state = customer_agent.CustomerAgentState.WAITING_FOR_FOOD


        # Filter and sort customers waiting for food
        waiting_customers = sorted(
            (a for a in self.model.agents_by_type[customer_agent.CustomerAgent]
             if a.state == customer_agent.CustomerAgentState.WAITING_FOR_FOOD),
            key=lambda c: c.time_left
        )

        # Get the customer with the smallest time_left
        if waiting_customers:
            customer = waiting_customers[0]

            # Only the specified amount of food can be processed at once.
            # The delay depends on the amount of customers
            preparation_delay = math.ceil(
                customer.num_people / int(self.model.config["Orders"]["parallel_preparation"])
            )

            # Occasionally introduce a probabilistic delay based on order_correctness
            random_delay = random.randint(0, int(self.model.config["Orders"]["delay_max"])) \
                if random.random() > float(self.model.config["Orders"]["delay_randomness"]) \
                else 0

            # Total delay combines the batch adjustment and random delay (if applicable)
            total_delay = preparation_delay + random_delay

            # Prepare the food
            if customer.food_preparation_time > 1 + total_delay:
                customer.food_preparation_time -= 1
            else:
                customer.state = customer_agent.CustomerAgentState.EATING
                customer.food_arrival_time = customer.time_left

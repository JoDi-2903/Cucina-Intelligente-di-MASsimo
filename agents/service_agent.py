from typing import Optional

from mesa import Agent, Model

from agents.customer_agent import CustomerAgent
from enums.customer_agent_state import CustomerAgentState
from models.config.config import Config
from models.config.logging_config import service_logger

logger = service_logger

class ServiceAgent(Agent):
    """An agent that represents the service in the restaurant"""

    def __init__(self, model: Model, customer_capacity: Optional[int] = None, salary_per_tick: Optional[float] = None):
        """
        Create a new service agent.

        Parameters:
            model: The model the agent belongs to.
            customer_capacity: The number of customers that can be served in parallel in one step.
            salary_per_tick: The salary of the service agent per tick.
        
        """
        super().__init__(model)
        self.salary_per_tick: float = salary_per_tick if salary_per_tick is not None else Config().service.service_agent_salary_per_tick
        self.customer_capacity: int = customer_capacity if customer_capacity is not None else Config().service.service_agent_capacity

        # Initialize the queue for customers. Queue is limited by capacity
        self.customer_queue: list[CustomerAgent] = []

    def weighted_sort_placing(self, customer: CustomerAgent):
        """ Custom sort key for sorting new customers by weighted criteria profit, waiting time and time left """
        return (
            (customer.dish.profit * customer.num_people) * Config().weights.rating_profit +
            customer.get_total_time() * Config().weights.rating_time_spent +
            customer.time_left * Config().weights.rating_time_left
        )

    def weighted_sort_serving(self, customer: CustomerAgent):
        """ Custom sort key for sorting already seated customers by weighted criteria profit, waiting time, time left and food preparation time """
        return (
            (customer.dish.profit * customer.num_people) * Config().weights.rating_profit +
            customer.get_total_time() * Config().weights.rating_time_spent +
            customer.time_left * Config().weights.rating_time_left +
            customer.food_preparation_time * Config().weights.rating_time_food_preparation
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
            key=self.weighted_sort_placing
        )

        # Get the customer with the smallest time_left
        if waiting_customers:
            customer: CustomerAgent = waiting_customers[0]

            # Check if the customer needs to be rejected
            if customer.dish.preparation_time + customer.dish.eating_time > customer.time_left:
                customer.state = CustomerAgentState.REJECTED

            # Check if the personal queue is full
            elif len(self.customer_queue) < Config().service.service_agent_capacity:
                # Add the customer to the queue and update their state
                self.customer_queue.append(customer)
                customer.state = CustomerAgentState.WAITING_FOR_FOOD

            logger.info("Step %d: Service agent %d is serving customer %d. Customer is currently %s",
                        self.model.steps, self.unique_id, customer.unique_id, customer.state)

        # Filter and sort customers waiting for food by weighted sort
        waiting_customers = sorted(
            (a for a in self.customer_queue if a.state == CustomerAgentState.WAITING_FOR_FOOD),
            key=self.weighted_sort_serving
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

            logger.info("Step %d: Service agent %d is serving customer %d. Customer is currently %s.",
                        self.model.steps, self.unique_id, customer.unique_id, customer.state)

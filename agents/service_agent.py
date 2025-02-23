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
        self.remaining_capacity: int = self.customer_capacity

        # Initialize the shift schedule dict[step] = bool
        self.shift_schedule: dict[int, bool] = {}

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
        # Don't do anything if the service agent is not scheduled to work
        if self.model.steps not in self.shift_schedule.keys() or not self.shift_schedule[self.model.steps]:
            return

        self._serve_customers()
        self._seat_customers()

        # Reset the remaining capacity for the next step
        self.remaining_capacity = self.customer_capacity



    def _seat_customers(self):
        """ Seat the customers that one service agent can serve """
        # Filter and sort new customers by weighted sort
        waiting_customers_placing = sorted(
            (a for a in self.model.agents_by_type[CustomerAgent]
             if a.state == CustomerAgentState.WAIT_FOR_SERVICE_AGENT),
            key=self.weighted_sort_placing,
            reverse=True
        )

        if waiting_customers_placing:
            # For each customer that the service agent can serve
            for customer in waiting_customers_placing[:self.remaining_capacity]:
                # Check if the customer needs to be rejected
                if customer.dish.preparation_time + customer.dish.eating_time > customer.time_left:
                    customer.state = CustomerAgentState.REJECTED

                # Seat the customers that one service agent can serve
                else:
                    customer.state = CustomerAgentState.WAITING_FOR_FOOD
                    self.__place_customer_in_grid(customer)

                self.remaining_capacity -= 1

                logger.info("Step %d: Service agent %d is serving customer %d. Customer is currently %s",
                            self.model.steps, self.unique_id, customer.unique_id, customer.state)

    def _serve_customers(self):
        """ Serve the customers that are already seated """
        # Filter and sort customers waiting for food by weighted sort
        waiting_customers_food = sorted(
            (a for a in self.model.agents_by_type[CustomerAgent]
             if a.state == CustomerAgentState.WAITING_FOR_FOOD),
            key=self.weighted_sort_serving,
            reverse=True
        )

        # Get the customer with the smallest time_left
        if waiting_customers_food:

            for customer in waiting_customers_food[:self.remaining_capacity]:
                # Prepare the food
                if customer.food_preparation_time > 1:
                    customer.food_preparation_time -= 1
                else:
                    customer.state = CustomerAgentState.EATING
                    customer.waiting_time = customer.init_time - customer.time_left

                self.remaining_capacity -= 1

                logger.info("Step %d: Service agent %d is serving customer %d. Customer is currently %s.",
                            self.model.steps, self.unique_id, customer.unique_id, customer.state)

    def __place_customer_in_grid(self, customer: CustomerAgent):
        """
        Place a customer in the grid at an empty position.
        :param customer: The customer agent to place in the grid of the restaurant model.
        """
        self.model.grid.move_to_empty(customer)
        logger.info("Step %d: Service agent %d placed customer %d in the grid.",
                    self.model.steps, self.unique_id, customer.unique_id)

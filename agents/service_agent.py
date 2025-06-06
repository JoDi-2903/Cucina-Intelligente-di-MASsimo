from typing import Optional

from mesa import Agent, Model

from agents.customer_agent import CustomerAgent
from data_structures.config.config import Config
from data_structures.config.logging_config import service_logger
from enums.customer_agent_state import CustomerAgentState

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

        # Initialize the shift schedule dict[step] = int
        self.shift_schedule: dict[int, int] = {}

    def step(self):
        # Don't do anything if the service agent is not scheduled to work
        if self.model.steps not in self.shift_schedule.keys() or self.shift_schedule[self.model.steps] == 0:
            return

        self.__serve_customers()
        self.__seat_customers()

        # Reset the remaining capacity for the next step
        self.remaining_capacity = self.customer_capacity

    def __serve_customers(self):
        """
        Serve the customers that are already seated
        """
        walked_distance = 0.0
        walked_capacity = 0
        customer: CustomerAgent or None = None
        for _ in range(self.remaining_capacity):
            # Break if there are no customers to serve
            if len(self.model.serve_route) == 0:
                break

            # Get next customer in the serve route and "walk" to them if needed
            if customer is None:
                # If no customer is currently being served, get the first customer in the serve route
                customer = self.model.serve_route[0]
            else:
                # If the service agent has already served a customer, the service agent will walk to the next customer which will affect the capacity
                next_customer = self.model.serve_route[0]
                walked_distance += self.__walk_to_customer(customer, next_customer)
                new_walked_capacity = walked_distance // 4
                if walked_capacity < new_walked_capacity:  # Decrease the capacity by 1 for every 5 units of distance
                    walked_capacity = new_walked_capacity
                    self.remaining_capacity -= 1
                customer = next_customer

            # If the service agent does not have enough capacity after walking, break
            if self.remaining_capacity == 0:
                break

            # Prepare the food
            if customer.food_preparation_time > 1:
                customer.food_preparation_time -= 1
            else:
                customer.state = CustomerAgentState.EATING
                customer.waiting_time = customer.init_time - customer.time_left

            # Update the remaining capacity and the route
            self.remaining_capacity -= 1
            self.model.serve_route.remove(customer)

            logger.info("Step %d: Service agent %d is serving customer %d. Customer is currently %s.",
                        self.model.steps, self.unique_id, customer.unique_id, customer.state)

    def __walk_to_customer(self, customer: CustomerAgent, next_customer: CustomerAgent):
        """
        Calculate the distance between the current position of the service agent (current customer) and the next customer.
        :param customer: The current customer agent that the service agent is serving.
        :param next_customer: The next customer agent that the service agent will serve.
        :return: The distance between the two customers.
        """
        # Iterate through the grid to find the positions
        customer_position: tuple[int, int] or None = None
        next_customer_position: tuple[int, int] or None = None
        for agent, position in self.model.grid.coord_iter():
            if agent == customer:
                customer_position = position
            elif agent == next_customer:
                next_customer_position = position

            # Break early if both positions are found
            if customer_position and next_customer_position:
                break

        # Check if both positions are found
        if customer_position is None or next_customer_position is None:
            return 0.0

        # Calculate the distance between the two positions
        return ((customer_position[0] - next_customer_position[0]) ** 2 +
                (customer_position[1] - next_customer_position[1]) ** 2) ** 0.5

    def __seat_customers(self):
        """ Seat the customers that one service agent can serve """
        for _ in range(self.remaining_capacity):
            # Break if there are no customers to seat
            if len(self.model.seat_route) == 0:
                break

            # Check if the customer needs to be rejected
            customer = self.model.seat_route[0]
            if Config().run.reject_unservable_customers and \
                customer.dish.preparation_time + customer.dish.eating_time > customer.time_left:
                customer.state = CustomerAgentState.REJECTED

            # Seat the customers that one service agent can serve
            else:
                customer.state = CustomerAgentState.WAITING_FOR_FOOD
                self.__place_customer_in_grid(customer)

            # Update the remaining capacity and the route
            self.remaining_capacity -= 1
            self.model.seat_route.remove(customer)

            logger.info("Step %d: Service agent %d is serving customer %d. Customer is currently %s",
                        self.model.steps, self.unique_id, customer.unique_id, customer.state)

    def __place_customer_in_grid(self, customer: CustomerAgent):
        """
        Place a customer in the grid at an empty position.
        :param customer: The customer agent to place in the grid of the restaurant model.
        """
        self.model.grid.move_to_empty(customer)
        logger.info("Step %d: Service agent %d placed customer %d in the grid.",
                    self.model.steps, self.unique_id, customer.unique_id)

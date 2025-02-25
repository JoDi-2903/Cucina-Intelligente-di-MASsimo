import numpy as np
from mesa import Agent, Model
from numpy import ndarray
from scipy import spatial
from sko.ACA import ACA_TSP

from agents.customer_agent import CustomerAgent
from data_structures.config.config import Config
from data_structures.config.logging_config import route_logger
from enums.customer_agent_state import CustomerAgentState
from enums.route_algorithm import RouteAlgorithm

logger = route_logger


class RouteAgent(Agent):
    def __init__(self, model: Model):
        """
        This simple reflex agent is responsible for managing the routes that the service agents take to serve/seat
        customers.
        """
        super().__init__(model)

    def step(self):
        """
        The route agent does not need to do anything in the step function.
        """
        # Create routes using the configured algorithm
        if Config().service.route_algorithm == RouteAlgorithm.WEIGHTED_SORT:
            serve_route, seat_route = self.__plan_serve_route_ws(), self.__plan_seat_route_ws()
        else:
            # The seat route is not a TSP so we can use the weighted sort algorithm for it
            serve_route, seat_route = self.__plan_serve_route_aco(), self.__plan_seat_route_ws()

        # Update the routes in the restaurant model
        self.model.serve_route = serve_route
        self.model.seat_route = seat_route

    # region Weighted Sort Algorithm

    def __plan_serve_route_ws(self) -> list[CustomerAgent]:
        """
        Plan the serve route for the service agents using the weighted sort algorithm.
        :return: A list of CustomerAgents representing the serve route.
        """
        return sorted(
            (a for a in self.model.agents_by_type[CustomerAgent]
             if a.state == CustomerAgentState.WAITING_FOR_FOOD),
            key=self.__weighted_sort_serving,
            reverse=True
        )

    @staticmethod
    def __weighted_sort_serving(customer: CustomerAgent):
        """Custom sort key for sorting already seated customers by weighted criteria profit, waiting time, time left and food preparation time"""
        return (
                (customer.dish.profit * customer.num_people) * Config().weights.rating_profit +
                customer.get_total_time() * Config().weights.rating_time_spent +
                customer.time_left * Config().weights.rating_time_left +
                customer.food_preparation_time * Config().weights.rating_time_food_preparation
        )

    def __plan_seat_route_ws(self) -> list[CustomerAgent]:
        """
        Plan the seat route for the service agents using the weighted sort algorithm.
        :return: A list of CustomerAgents representing the seat route.
        """
        return sorted(
            (a for a in self.model.agents_by_type[CustomerAgent]
             if a.state == CustomerAgentState.WAIT_FOR_SERVICE_AGENT),
            key=self.__weighted_sort_seating,
            reverse=True
        )

    @staticmethod
    def __weighted_sort_seating(customer: CustomerAgent):
        """Custom sort key for sorting new customers by weighted criteria profit, waiting time and time left."""
        return (
                (customer.dish.profit * customer.num_people) * Config().weights.rating_profit +
                customer.get_total_time() * Config().weights.rating_time_spent +
                customer.time_left * Config().weights.rating_time_left
        )

    # endregion

    # region ACO Algorithm

    def __plan_serve_route_aco(self) -> list[CustomerAgent]:
        """
        Plan a serve route using the ant colony optimization algorithm.
        :return: A list of CustomerAgents representing the serve route.
        """
        # Calculate the distance matrix for the ACO algorithm by calculating the Euclidean distance between the occupied
        # tables. The occupied tables are determined by restaurant's grid.
        occupied_tables: ndarray = np.column_stack(np.nonzero(self.model.grid.empty_mask is False))
        distance_matrix = spatial.distance.cdist(occupied_tables, occupied_tables, metric='euclidean')

        # Run the ACO algorithm to calculate the best seat route and the best seat distance
        aca = ACA_TSP(
            func=lambda routine: self.__calculate_tour_distance(routine, distance_matrix),
            n_dim=len(occupied_tables),
            size_pop=50,
            max_iter=200,
            distance_matrix=distance_matrix
        )
        serve_route_aco, best_serve_distance = aca.run()

        # Log the best serve distance
        route_logger.info(f"Step {self.model.steps}: Best serve distance: {best_serve_distance}")

        return serve_route_aco

    @staticmethod
    def __calculate_tour_distance(routine, distance_matrix: ndarray) -> float:
        """
        Calculate the total distance of the passed route for the ACO algorithm.
        :param routine: The routine to calculate the total distance for.
        :return: The total distance of the route.
        """
        num_points, = routine.shape
        return sum([distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] for i in
                    range(num_points)])

    # endregion

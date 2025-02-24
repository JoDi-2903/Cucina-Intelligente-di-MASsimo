import numpy as np
from mesa import Agent, Model
from numpy import ndarray
from scipy import spatial
from scipy.spatial import distance_matrix
from sko.ACA import ACA_TSP

from agents.customer_agent import CustomerAgent
from agents.service_agent import ServiceAgent
from data_structures.config.config import Config
from enums.customer_agent_state import CustomerAgentState
from enums.route_algorithm import RouteAlgorithm


class RouteAgent(Agent):
    def __init__(self, model: Model):
        """
        This simple reflex agent is responsible for managing the routes that the service agents take to serve/seat
        customers.
        """
        super().__init__(model)
        self.__serve_distance_matrix: ndarray
        self.__seat_distance_matrix: ndarray

    def step(self):
        """
        The route agent does not need to do anything in the step function.
        """
        # Create routes using the configured algorithm
        if Config().service.route_algorithm == RouteAlgorithm.WEIGHTED_SORT:
            serve_route, seat_route = self.__plan_routes_weighted_sort()
        else:
            serve_route, seat_route = self.__plan_routes_aco()

        # Update the routes in the restaurant model
        self.model.serve_route = serve_route
        self.model.seat_route = seat_route

    # region Weighted Sort Algorithm

    def __plan_routes_weighted_sort(self) -> tuple[list[CustomerAgent], list[CustomerAgent]]:
        """
        Plan the routes for the service agents using the weighted sort algorithm.
        :return: A tuple of the serve and seat routes as lists of CustomerAgents.
        """
        serve_route_ws: list[CustomerAgent] = sorted(
            (a for a in self.model.agents_by_type[CustomerAgent]
             if a.state == CustomerAgentState.WAITING_FOR_FOOD),
            key=self.__weighted_sort_serving,
            reverse=True
        )
        seat_route_ws: list[CustomerAgent] = sorted(
            (a for a in self.model.agents_by_type[CustomerAgent]
             if a.state == CustomerAgentState.WAIT_FOR_SERVICE_AGENT),
            key=self.__weighted_sort_seating,
            reverse=True
        )

        return serve_route_ws, seat_route_ws

    @staticmethod
    def __weighted_sort_serving(customer: CustomerAgent):
        """Custom sort key for sorting already seated customers by weighted criteria profit, waiting time, time left and food preparation time"""
        return (
                (customer.dish.profit * customer.num_people) * Config().weights.rating_profit +
                customer.get_total_time() * Config().weights.rating_time_spent +
                customer.time_left * Config().weights.rating_time_left +
                customer.food_preparation_time * Config().weights.rating_time_food_preparation
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
    # TODO: ACO MAKES ONLY SENSE IF ONE SERVICE AGENT IS ACTIVE BECAUSE ONLY ONE WOULD "WALK" THE CALCULATED ROUTE. SOLUTION: ASSIGN TABLES TO EACH SERVICE AGENT AND CALCULATE ROUTE FOR EACH SERVICE AGENT
    def __plan_routes_aco(self) -> tuple[list[CustomerAgent], list[CustomerAgent]]:
        """
        Plan the routes for the service agents using the ACO algorithm. The distance matrix is calculated using the
        total distance function and grid coordinates.
        :return: A tuple of the serve and seat routes as lists of CustomerAgents.
        """
        # Get a mask of empty cells to calculate the occupied and free tables
        empty_mask: ndarray = self.model.grid.empty_mask
        occupied_tables: ndarray = np.column_stack(np.nonzero(empty_mask is False))
        free_tables: ndarray = np.column_stack(np.nonzero(empty_mask is True))

        # Assign tables to each service agent and calculate the route for each service agent TODO
        for service_agent in self.model.agents_by_type[ServiceAgent]:
            # Calculate the serve distance matrix for the ACO algorithm using the Euclidean distance
            self.__serve_distance_matrix = spatial.distance.cdist(occupied_tables, occupied_tables, metric='euclidean')

            aca_serve = ACA_TSP(func=self.__calculate_serve_tour_distance, n_dim=len(occupied_tables),
                                size_pop=50, max_iter=200,
                                distance_matrix=distance_matrix)

            best_x, best_y = aca_serve.run()
            return best_points, best_distance

        # Calculate the serve distance matrix for the ACO algorithm using the Euclidean distance
        self.__serve_distance_matrix = spatial.distance.cdist(occupied_tables, occupied_tables, metric='euclidean')

        aca_serve = ACA_TSP(func=self.__calculate_serve_tour_distance, n_dim=len(occupied_tables),
                            size_pop=50, max_iter=200,
                            distance_matrix=distance_matrix)

        best_x, best_y = aca_serve.run()
        return best_points, best_distance

    def __calculate_serve_tour_distance(self, routine) -> float:
        """
        Calculate the total distance of the passed route for the ACO algorithm.
        :param routine: The routine to calculate the total distance for.
        :return: The total distance of the route.
        """
        num_points, = routine.shape
        return sum([self.__serve_distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] for i in range(num_points)])

    def __calculate_seat_tour_distance(self, routine) -> float:
        """
        Calculate the total distance of the passed route for the ACO algorithm.
        :param routine: The routine to calculate the total distance for.
        :return: The total distance of the route.
        """
        num_points, = routine.shape
        return sum([self.__serve_distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] for i in range(num_points)])

# endregion

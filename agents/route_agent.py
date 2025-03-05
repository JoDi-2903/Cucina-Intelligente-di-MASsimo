import numpy as np
from acopy import Solver, Colony, Solution
from mesa import Agent, Model
from networkx.classes import Graph

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
        # Get the coordinates of all occupied tables from the restaurant's grid as a list of tuples
        occupied_tables: list[tuple[int, int]] = self.__get_occupied_tables()
        if len(occupied_tables) == 0:
            return []

        # If only one table is occupied, return the customer at that table
        elif len(occupied_tables) == 1:
            return [self.model.grid[occupied_tables[0]]]

        # Create a graph with the occupied tables as nodes for the ACO algorithm to solve
        graph = self.__create_graph(occupied_tables)

        # Solve the TSP using the ACO algorithm
        solution = self.__aco_solve(graph)

        # Get list of CustomerAgents from the solution nodes
        serve_route_aco: list[CustomerAgent] = [self.model.grid[i] for i in solution.nodes]

        # Log the best serve distance
        route_logger.info(f"Step {self.model.steps}: Best serve distance: {solution.cost}")
        route_logger.info(f"Step {self.model.steps}: Best serve route: {solution.nodes}\n")

        return serve_route_aco

    def __get_occupied_tables(self) -> list[tuple[int, int]]:
        """
        Get the coordinates of all occupied tables from the restaurant's grid.
        :return: A list of tuples representing the coordinates of the occupied tables.
        """
        # Get the coordinates of all occupied tables from the restaurant's grid using the empty mask
        occupied_tables_lists: list[list[int, int]] = np.column_stack(
            np.nonzero(self.model.grid.empty_mask == False)
        ).tolist()

        # Remove all customer agents from the list that are in the state of EATING
        customer_agents: list[CustomerAgent] = [self.model.grid[i] for i in occupied_tables_lists]
        waiting_customer_agents: list[CustomerAgent] = [agent for agent in customer_agents if
                                                        agent.state == CustomerAgentState.WAITING_FOR_FOOD]

        # Return the coordinates of the occupied tables
        nodes: list[tuple[int, int]] = [
            (table[0], table[1]) for table in occupied_tables_lists if
            self.model.grid[table] in waiting_customer_agents
        ]

        return nodes

    @staticmethod
    def __create_graph(occupied_tables: list[tuple[int, int]]) -> Graph:
        """
        Initialize a networkx graph for the ACO algorithm.
        :param occupied_tables: A list of tuples representing the coordinates of the occupied tables.
        :return: A networkx graph with the occupied tables as nodes and the Euclidean distance between them as edges.
        """
        # Create a networkx graph and add the occupied tables as nodes to the graph
        graph = Graph()
        graph.add_nodes_from(occupied_tables)

        # Add edges between all nodes
        edges = [
            (occupied_tables[i], occupied_tables[j])
            for i in range(len(occupied_tables))
            for j in range(i + 1, len(occupied_tables))
        ]
        graph.add_edges_from(edges)

        # Add the Euclidean distance between two nodes as the weight of the edge
        for u, v in graph.edges():
            weight = np.linalg.norm(np.array(u) - np.array(v))
            graph[u][v]['weight'] = weight

        return graph

    @staticmethod
    def __aco_solve(graph: Graph) -> Solution:
        """
        Solve the ACO algorithm for the given graph.
        :param graph: A networkx graph representing the occupied tables in the restaurant.
        """
        solver = Solver(
            rho=.03,  # Percentage of pheromone to evaporate each iteration
            q=1  # Amount of pheromone an ant can deposit on a node
        )
        colony = Colony(
            alpha=1,  # Relative importance of pheromones
            beta=2  # Relative importance of edge weight
        )

        return solver.solve(graph, colony, limit=100)

    # endregion

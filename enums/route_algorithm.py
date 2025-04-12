from enum import Enum


class RouteAlgorithm(Enum):
    ACO = 0,
    WEIGHTED_SORT = 1,

    @staticmethod
    def get_from_str(value: str):
        """
        Get the route algorithm from the given string value.
        :param value: The string value of the route algorithm.
        :return: The route algorithm if found, otherwise the default route algorithm (ACO).
        """
        for route_algorithm in RouteAlgorithm:
            if route_algorithm.name == value.upper():
                return route_algorithm

        return RouteAlgorithm.ACO

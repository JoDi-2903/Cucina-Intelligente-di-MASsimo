from enums.route_algorithm import RouteAlgorithm


class ServiceSettings:
    """
    This class stores the service configurations of the system.
    """

    def __init__(self, config: dict[str, int or str] = None):
        """
        Initialize the service object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.service_agents: int = config["service_agents"]
            self.__service_agent_capacity: int = config["service_agent_capacity"]
            self.__service_agent_salary_per_tick: float = config["service_agent_salary_per_tick"]
            self.__service_agent_capacity_min: int = config["service_agent_capacity_min"]
            self.__service_agent_capacity_max: int = config["service_agent_capacity_max"]
            self.__route_algorithm: RouteAlgorithm = RouteAlgorithm.get_from_str(config["route_algorithm"])
        else:
            raise ValueError("No default values for service settings available.")

    @property
    def service_agent_capacity(self) -> int:
        return self.__service_agent_capacity

    @property
    def service_agent_salary_per_tick(self) -> float:
        return self.__service_agent_salary_per_tick

    @property
    def service_agent_capacity_min(self) -> int:
        return self.__service_agent_capacity_min

    @property
    def service_agent_capacity_max(self) -> int:
        return self.__service_agent_capacity_max

    @property
    def route_algorithm(self) -> RouteAlgorithm:
        return self.__route_algorithm

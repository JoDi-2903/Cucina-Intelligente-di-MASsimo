class ServiceSettings:
    """
    This class stores the service configurations of the system.
    """

    def __init__(self, config: dict[str, int] = None):
        """
        Initialize the service object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.service_agents: int = config["service_agents"]
            self.__service_agent_capacity: int = config["service_agent_capacity"]
        else:
            self.service_agents: int = 5
            self.__service_agent_capacity: int = 5

    @property
    def service_agent_capacity(self) -> int:
        return self.__service_agent_capacity

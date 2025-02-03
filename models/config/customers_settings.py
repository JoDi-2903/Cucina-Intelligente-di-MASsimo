class CustomersSettings:
    """
    Class to store the customer configurations.
    """

    def __init__(self, config: dict[str, int] = None):
        """
        Initialize the customer object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.__customer_agents: int = config["customer_agents"]
            self.__max_customers_per_agent: int = config["max_customers_per_agent"]
            self.__time_min: int = config["time_min"]
            self.__time_max: int = config["time_max"]
        else:
            self.__customer_agents: int = 100
            self.__max_customers_per_agent: int = 15
            self.__time_min: int = 20
            self.__time_max: int = 100

    @property
    def customer_agents(self) -> int:
        return self.__customer_agents

    @property
    def max_customers_per_agent(self) -> int:
        return self.__max_customers_per_agent

    @property
    def time_min(self) -> int:
        return self.__time_min

    @property
    def time_max(self) -> int:
        return self.__time_max

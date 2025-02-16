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
            self.__max_simultaneous_customers_in_restaurant: int = config["max_simultaneous_customers_in_restaurant"]
            self.__max_new_customer_agents_per_step: int = config["max_new_customer_agents_per_step"]
            self.__max_customers_per_agent: int = config["max_customers_per_agent"]
            self.__time_min: int = config["time_min"]
            self.__time_max: int = config["time_max"]
        else:
            raise ValueError("No default values for customers settings available.")

    @property
    def max_simultaneous_customers_in_restaurant(self) -> int:
        return self.__max_simultaneous_customers_in_restaurant

    @property
    def max_new_customer_agents_per_step(self) -> int:
        return self.__max_new_customer_agents_per_step

    @property
    def max_customers_per_agent(self) -> int:
        return self.__max_customers_per_agent

    @property
    def time_min(self) -> int:
        return self.__time_min

    @property
    def time_max(self) -> int:
        return self.__time_max

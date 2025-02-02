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
            self.customer_agents: int = config["customer_agents"]
            self.max_customers_per_agent: int = config["max_customers_per_agent"]
            self.time_min: int = config["time_min"]
            self.time_max: int = config["time_max"]
        else:
            self.customer_agents: int = 100
            self.max_customers_per_agent: int = 15
            self.time_min: int = 20
            self.time_max: int = 100

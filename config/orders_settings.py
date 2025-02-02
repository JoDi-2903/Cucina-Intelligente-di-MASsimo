class OrdersSettings:
    """
    Class to store the configuration of the orders in the restaurant.
    """

    def __init__(self, config: dict[str, int or float] = None):
        """
        Initialize the order object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.order_correctness: float = config["order_correctness"]
            self.parallel_preparation: int = config["parallel_preparation"]
            self.delay_randomness: float = config["delay_randomness"]
            self.delay_max: int = config["delay_max"]
        else:
            self.order_correctness: float = 0.9
            self.parallel_preparation: int = 5
            self.delay_randomness: float = 0.8
            self.delay_max: int = 10

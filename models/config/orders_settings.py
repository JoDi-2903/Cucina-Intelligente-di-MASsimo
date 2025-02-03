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
            self.__order_correctness: float = config["order_correctness"]
            self.__parallel_preparation: int = config["parallel_preparation"]
            self.__delay_randomness: float = config["delay_randomness"]
            self.__delay_max: int = config["delay_max"]
        else:
            self.__order_correctness: float = 0.9
            self.__parallel_preparation: int = 5
            self.__delay_randomness: float = 0.8
            self.__delay_max: int = 10

    @property
    def order_correctness(self) -> float:
        return self.__order_correctness

    @property
    def parallel_preparation(self) -> int:
        return self.__parallel_preparation

    @property
    def delay_randomness(self) -> float:
        return self.__delay_randomness

    @property
    def delay_max(self) -> int:
        return self.__delay_max

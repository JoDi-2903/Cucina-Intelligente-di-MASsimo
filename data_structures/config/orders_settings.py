class OrdersSettings:
    """
    Class to store the configuration of the orders in the restaurant.
    """

    def __init__(self, config: dict[str, int | float] = None):
        """
        Initialize the order object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.__order_correctness: float = config["order_correctness"]
            self.__parallel_preparation: int = config["parallel_preparation"]
        else:
            raise ValueError("No default values for orders settings available.")

    @property
    def order_correctness(self) -> float:
        return self.__order_correctness

    @property
    def parallel_preparation(self) -> int:
        return self.__parallel_preparation

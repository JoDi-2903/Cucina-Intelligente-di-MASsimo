class WeightsSettings:
    """
    This class stores the weight configurations of the system.
    """

    def __init__(self, config: dict[str, int or float] = None):
        """
        Initialize the weights object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.__time_exceeding: float = config["time_exceeding"]
            self.__order_error: int = config["order_error"]
        else:
            self.__time_exceeding: float = 0.005
            self.__order_error: int = 2

    @property
    def time_exceeding(self) -> float:
        return self.__time_exceeding

    @property
    def order_error(self) -> int:
        return self.__order_error

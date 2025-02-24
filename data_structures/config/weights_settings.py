class WeightsSettings:
    """
    This class stores the weight configurations of the system.
    """

    def __init__(self, config: dict[str, int | float] = None):
        """
        Initialize the weights object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.__time_exceeding: float = config["time_exceeding"]
            self.__order_error: int = config["order_error"]
            self.__rating_profit: float = config["rating_profit"]
            self.__rating_time_spent: float = config["rating_time_spent"]
            self.__rating_time_left: float = config["rating_time_left"]
            self.__rating_time_food_preparation: float = config["rating_time_food_preparation"]
        else:
            raise ValueError("No default values for weights settings available.")

    @property
    def time_exceeding(self) -> float:
        return self.__time_exceeding

    @property
    def order_error(self) -> int:
        return self.__order_error

    @property
    def rating_profit(self) -> float:
        return self.__rating_profit

    @property
    def rating_time_spent(self) -> float:
        return self.__rating_time_spent

    @property
    def rating_time_left(self) -> float:
        return self.__rating_time_left

    @property
    def rating_time_food_preparation(self) -> float:
        return self.__rating_time_food_preparation

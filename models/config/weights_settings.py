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
            self.__rating_waiting_time: float = config["rating_waiting_time"]
            self.__rating_total_time: float = config["rating_total_time"]
            self.__rating_num_people: float = config["rating_num_people"]
        else:
            self.__time_exceeding: float = 0.005
            self.__order_error: int = 2
            self.__rating_profit: float = 1.0
            self.__rating_waiting_time: float = 0.7
            self.__rating_total_time: float = 0.5
            self.__rating_num_people: float = 0.3
            # TODO: do we really have to add the default values again? Why not just use the default values in the config...?

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
    def rating_waiting_time(self) -> float:
        return self.__rating_waiting_time

    @property
    def rating_total_time(self) -> float:
        return self.__rating_total_time

    @property
    def rating_num_people(self) -> float:
        return self.__rating_num_people

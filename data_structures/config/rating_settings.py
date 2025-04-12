from enums.rating_strategy import RatingStrategy

class RatingSettings:
    """
    This class stores the rating configurations of the system.
    """

    def __init__(self, config: dict[str, int] = None):
        """
        Initialize the rating object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.__rating_default: int = config["rating_default"]
            self.__rating_min: int = config["rating_min"]
            self.__rating_max: int = config["rating_max"]
            self.__rating_strategy: RatingStrategy = RatingStrategy.get_from_str(config["rating_strategy"])
        else:
            raise ValueError("No default values for rating settings available.")

    @property
    def rating_default(self) -> int:
        return self.__rating_default

    @property
    def rating_min(self) -> int:
        return self.__rating_min

    @property
    def rating_max(self) -> int:
        return self.__rating_max

    @property
    def rating_strategy(self) -> RatingStrategy:
        return self.__rating_strategy

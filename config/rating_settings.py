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
            self.rating_default: int = config["rating_default"]
            self.rating_min: int = config["rating_min"]
            self.rating_max: int = config["rating_max"]
        else:
            self.rating_default: int = 5
            self.rating_min: int = 0
            self.rating_max: int = 5

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
            self.time_exceeding: float = config["time_exceeding"]
            self.order_error: int = config["order_error"]
        else:
            self.time_exceeding: float = 0.005
            self.order_error: int = 2

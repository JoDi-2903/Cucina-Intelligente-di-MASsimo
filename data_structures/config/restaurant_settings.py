class RestaurantSettings:
    """
    Class to store the restaurant settings.
    """

    def __init__(self, config: dict[str, int] = None):
        """
        Initialize the restaurant object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            # The grid width and height are used to visualize the restaurant in a grid and determine the maximum capacity of customer agents in the restaurant.
            self.__grid_width: int = config["grid_width"]
            self.__grid_height: int = config["grid_height"]
        else:
            raise ValueError("No default values for restaurant settings available.")

    @property
    def grid_width(self) -> int:
        return self.__grid_width

    @property
    def grid_height(self) -> int:
        return self.__grid_height

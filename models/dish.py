class Dish:
    """
    Dish class represents a dish in the restaurant.
    """

    def __init__(self, name: str, preparation_time: int, eating_time: int, profit: float):
        """
        Initialize a dish with the given parameters.
        :param name: The name of the dish
        :param preparation_time: The time needed to prepare the dish (in ticks)
        :param eating_time: The time needed to eat the dish (in ticks)
        :param profit: The profit made by selling the dish
        """
        self.name: str = name
        self.preparation_time: int = preparation_time
        self.eating_time: int = eating_time
        self.profit: float = profit

    def __str__(self):
        return self.name

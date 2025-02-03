import json
import os

from models.dish import Dish


class Menu:
    """
    Menu class represents the menu of the restaurant. It contains a list of all available dishes.
    """

    def __init__(self):
        """
        Initialize the menu by reading the menu from the menu json file.
        """
        # Read menu from file
        file_path = os.path.join('data', 'menu.json')
        try:
            with open(file=file_path, mode="r", encoding="utf8") as file:
                self.json_content = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The menu file could not be found in the given path: {file_path}")

        # Initialize the dishes
        self.dishes: list[Dish] = []
        for json_dish in self.json_content['menu']:
            dish = Dish(json_dish['name'], json_dish['preparationTime'], json_dish['eatingTime'], json_dish['profit'])
            self.dishes.append(dish)

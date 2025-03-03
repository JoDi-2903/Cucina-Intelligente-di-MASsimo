import json
import os

from data_structures.config.customers_settings import CustomersSettings
from data_structures.config.orders_settings import OrdersSettings
from data_structures.config.rating_settings import RatingSettings
from data_structures.config.research_settings import ResearchSettings
from data_structures.config.restaurant_settings import RestaurantSettings
from data_structures.config.run_settings import RunSettings
from data_structures.config.service_settings import ServiceSettings
from data_structures.config.weights_settings import WeightsSettings
from meta_classes.singleton import SingletonMeta


class Config(metaclass=SingletonMeta):
    """
    This class stores the configurations of the system.
    """

    def __init__(self):
        """
        Initialize the config object with the
        """
        # Try to read the config file.
        json_content: dict = self.__read_config_file()

        # Initialize the settings with the values from the file.
        self.__rating = RatingSettings(json_content["Rating"])
        self.__orders = OrdersSettings(json_content["Orders"])
        self.__weights = WeightsSettings(json_content["Weights"])
        self.__restaurant = RestaurantSettings(json_content["Restaurant"])
        self.__customers = CustomersSettings(json_content["Customers"])
        self.__service = ServiceSettings(json_content["Service"])
        self.__research = ResearchSettings(json_content["Research"])
        self.__run = RunSettings(json_content["Run"])

    @staticmethod
    def __read_config_file() -> dict:
        """ Try to load configurations from config file. If there is no file, raise an error. """
        try:
            with open(os.path.join("data", "config.json"), mode="r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError("Config file `config.json` not found.") from e

    @property
    def rating(self) -> RatingSettings:
        return self.__rating

    @property
    def orders(self) -> OrdersSettings:
        return self.__orders

    @property
    def weights(self) -> WeightsSettings:
        return self.__weights

    @property
    def restaurant(self) -> RestaurantSettings:
        return self.__restaurant

    @property
    def customers(self) -> CustomersSettings:
        return self.__customers

    @property
    def service(self) -> ServiceSettings:
        return self.__service

    @property
    def research(self) -> ResearchSettings:
        return self.__research

    @property
    def run(self) -> RunSettings:
        return self.__run

import json
import os

from meta_classes.singleton import SingletonMeta
from models.config.customers_settings import CustomersSettings
from models.config.orders_settings import OrdersSettings
from models.config.rating_settings import RatingSettings
from models.config.run_settings import RunSettings
from models.config.service_settings import ServiceSettings
from models.config.weights_settings import WeightsSettings


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
        self.__customers = CustomersSettings(json_content["Customers"])
        self.__service = ServiceSettings(json_content["Service"])
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
    def customers(self) -> CustomersSettings:
        return self.__customers

    @property
    def service(self) -> ServiceSettings:
        return self.__service

    @property
    def run(self) -> RunSettings:
        return self.__run

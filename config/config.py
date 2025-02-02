import json
import os

from config.customers_settings import CustomersSettings
from config.orders_settings import OrdersSettings
from config.rating_settings import RatingSettings
from config.run_settings import RunSettings
from config.service_settings import ServiceSettings
from config.weights_settings import WeightsSettings


class Config:
    """
    This class stores the configurations of the system.
    """

    def __init__(self):
        """
        Initialize the config object with the default values.
        """
        self.rating = RatingSettings()
        self.orders = OrdersSettings()
        self.weights = WeightsSettings()
        self.customers = CustomersSettings()
        self.service = ServiceSettings()
        self.run = RunSettings()


CONFIG: Config = Config()


def init_config() -> None:
    """
    Initialize the config object with the values from the config file.
    """
    # Try to load configurations from config file. If there is no file, return to use the default values.
    try:
        with open(os.path.join("data", "config.json"), mode="r", encoding="utf-8") as f:
            config: dict = json.load(f)
    except FileNotFoundError:
        print("Config file not found.")
        return

    # Update the settings of the global config variable with the loaded values.
    global CONFIG
    CONFIG.rating = RatingSettings(config["Rating"])
    CONFIG.orders = OrdersSettings(config["Orders"])
    CONFIG.weights = WeightsSettings(config["Weights"])
    CONFIG.customers = CustomersSettings(config["Customers"])
    CONFIG.service = ServiceSettings(config["Service"])
    CONFIG.run = RunSettings(config["Run"])

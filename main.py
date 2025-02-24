import sys
import threading

from ml.lstm_model import LSTMModel
from data_structures.config import Config
from data_structures.history import History
from visualization.dashboard import Dashboard

# Create a global history object to track the data
history = History()

# Create the dashboard
dashboard = Dashboard()


def run_restaurant():
    """Run the restaurant model and emit updates to the dashboard."""
    # Lazy import to avoid partial initialization
    from models.restaurant_model import RestaurantModel

    # Create the restaurant model and the machine learning model
    lstm_model = LSTMModel()
    restaurant = RestaurantModel(lstm_model)

    # Iterate over the steps of the restaurant model
    while restaurant.running and (restaurant.steps < Config().run.step_amount or Config().run.endless_mode):
        restaurant.step()


def is_running_in_debug_mode():
    """
    Check if the program is running in debug mode.
    :return: True if the program is running in debug mode, False otherwise
    """
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None


if __name__ == "__main__":
    # Start the restaurant in a separate thread
    threading.Thread(target=run_restaurant).start()

    # Run the Dash server in the main thread
    dashboard.run(is_running_in_debug_mode())

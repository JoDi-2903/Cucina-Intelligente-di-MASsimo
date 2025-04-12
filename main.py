import sys
import threading

from data_structures.config.config import Config
from data_structures.history import History
from ml.lstm_model import LSTMModel
from visualization.dashboard import Dashboard
from helper.service_agent_calculator import calculate_minimal_service_agents
from termcolor import colored

# Create a global history object to track the data
history = History()

# Create the dashboard
dashboard = Dashboard()


def run_restaurant():
    """Run the restaurant model and emit updates to the dashboard."""
    # Lazy import to avoid partial initialization
    from models.restaurant_model import RestaurantModel

    # Create the restaurant model and the machine learning model
    lstm_model = LSTMModel(pretrained_csv_path='ml/train_data.csv', pretrain_epochs=Config().run.pretrain_epochs)
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

    try:
        config_service_agents = Config().service.service_agents
        recommended_service_agents = calculate_minimal_service_agents()
        if config_service_agents < recommended_service_agents:
            print(colored(f"\n\n\nWarning: The number of service agents in the configuration ({config_service_agents}) is below the recommended number ({recommended_service_agents}). The optimization might be infeasible!\n\n\n", "yellow"))
    except Exception:
        pass

    # Start the restaurant in a separate thread
    threading.Thread(target=run_restaurant).start()

    # Run the Dash server in the main thread
    dashboard.run(is_running_in_debug_mode())

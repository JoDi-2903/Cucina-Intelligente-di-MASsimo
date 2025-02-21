import threading

from ml.lstm_model import LSTMModel
from models.config.config import Config
from models.history import History
from visualization.dashboard import Dashboard

# Create a global history object to track the data
history = History()

# Create the dashboard
dashboard = Dashboard()


def run_restaurant():
    """Run the restaurant model and emit updates to the dashboard."""
    # Create the restaurant model and the machine learning model
    from models.restaurant_model import RestaurantModel  # Lazy import to avoid circular dependencies
    lstm_model = LSTMModel()
    restaurant = RestaurantModel(lstm_model)

    # Iterate over the steps of the restaurant model
    while restaurant.running and restaurant.steps < Config().run.step_amount:
        restaurant.step()


if __name__ == "__main__":
    # Start the restaurant in a separate thread
    threading.Thread(target=run_restaurant).start()

    # Run the Dash server in the main thread
    dashboard.run()

# TODO: Ausarbeitung + Präsentation

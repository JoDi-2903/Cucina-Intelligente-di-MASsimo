import threading

from ml.lstm_model import LSTMModel
from models.config.config import Config
from models.restaurant_model import RestaurantModel
from visualization.dashboard import Dashboard

# Create machine learning model
lstm_model = LSTMModel()

# Create the Mesa Model
restaurant = RestaurantModel(lstm_model)

# Create the dashboard
dashboard = Dashboard()


def run_restaurant():
    """Run the restaurant model and emit updates to the dashboard."""
    while restaurant.running and restaurant.steps < Config().run.step_amount:
        restaurant.step()


if __name__ == "__main__":
    # Start the restaurant in a separate thread
    threading.Thread(target=run_restaurant).start()

    # Run the Dash server in the main thread
    dashboard.run()

# TODO: Ausarbeitung + Präsentation

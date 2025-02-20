from ml.lstm_model import LSTMModel
from models.config.config import Config
from models.restaurant_model import RestaurantModel

if __name__ == "__main__":
    # Create machine learning model
    lstm_model = LSTMModel()

    # Create the Mesa Model
    restaurant = RestaurantModel(lstm_model)

    while restaurant.running and restaurant.steps < Config().run.step_amount:
        restaurant.step()
        wait_time, profit = restaurant.evaluate()

# TODO DN: GUI mit live Diagrammen - Mesa Grid (max. Anzahl Kunden, Heatmap mäßig anzeigen) - Statistiken!
# TODO: Ausarbeitung + Präsentation
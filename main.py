import json
import threading

from flask import Flask
from flask_socketio import SocketIO

from ml.lstm_model import LSTMModel
from models.config.config import Config
from models.restaurant_model import RestaurantModel
from visualization.dashboard import Dashboard
from visualization.messages.agents_message import AgentsMessage
from visualization.messages.dashboard_message import DashboardMessage
from visualization.messages.profit_message import ProfitMessage
from visualization.messages.time_spent_message import TimeSpentMessage

# Create machine learning model
lstm_model = LSTMModel()

# Create the Mesa Model
restaurant = RestaurantModel(lstm_model)

# Initialize Flask app and SocketIO
server = Flask(__name__)
socketio = SocketIO(server, cors_allowed_origins="*")

# Create the dashboard
dashboard = Dashboard(server)


def emit_dashboard_updates():
    """Emit updates to the dashboard."""
    # Lazy import to avoid partial initializations
    from agents.customer_agent import CustomerAgent
    from agents.manager_agent import ManagerAgent
    from agents.service_agent import ServiceAgent

    agent_message = AgentsMessage(
        num_agents=len(restaurant.agents),
        num_customer_agents=len(restaurant.agents_by_type[CustomerAgent]),
        num_service_agents=len(restaurant.agents_by_type[ServiceAgent]),
        num_manager_agents=len(restaurant.agents_by_type[ManagerAgent])
    )
    profit_message = ProfitMessage(
        profit_growth=list(restaurant.profit_per_step.values())
    )
    time_spent_message = TimeSpentMessage(
        total_time_spent=restaurant.total_time_spent,
        total_waiting_time=restaurant.waiting_time_spent,
        num_customer_agens=len(restaurant.agents_by_type[CustomerAgent])
    )
    dashboard_message = DashboardMessage(
        step=restaurant.steps,
        agent_message=agent_message,
        profit_message=profit_message,
        time_spent_message=time_spent_message
    )

    socketio.emit('update_graph', dashboard_message.to_dict())


def run_restaurant():
    """Run the restaurant model and emit updates to the dashboard."""
    # Create the Flask app and the SocketIO instance that will be used to communicate with the dashboard
    socketio.run(server, debug=True, port=8081, allow_unsafe_werkzeug=True, threaded=True)

    while restaurant.running and restaurant.steps < Config().run.step_amount:
        restaurant.step()
        wait_time, profit = restaurant.evaluate()
        emit_dashboard_updates()


if __name__ == "__main__":
    # Start the restaurant in a separate thread
    threading.Thread(target=run_restaurant).start()

    # Run the Dash server in the main thread
    dashboard.run()

# TODO: Ausarbeitung + Präsentation

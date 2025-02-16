import pyoptinterface as poi
import numpy as np
from pyoptinterface import highs

from mesa_objects.models.restaurant_model import RestaurantModel
from ml.lstm_model import LSTMModel
from models.config.config import Config


def objective_function(x: np.ndarray) -> tuple[int, float]:
    """
    Objective function to minimize the total waiting time in the restaurant
    :param service_agents: Number of service agents
    """
    # Create machine learning model
    lstm_model = LSTMModel()

    # Create the Mesa Model
    restaurant = RestaurantModel()
    restaurant.lstm_model = lstm_model

    for i in x:
        # Set the number of service agents and parallel preparation according to the optimization
        Config().service.service_agents = int(i)

        # Run the model with the updated configuration
        while restaurant.running and restaurant.steps < Config().run.step_amount:
            restaurant.step()
            wait_time, profit = restaurant.evaluate()

    return (wait_time, profit)


if __name__ == "__main__":
    # Create model that solves optimization problems
    opt_model = highs.Model()

    SIMULATION_STEPS = 50
    x0 = np.ones(SIMULATION_STEPS) * 5  # Start mit 5 Agenten pro Zeitschritt
    lb = np.ones(SIMULATION_STEPS) * 1  # Mindestens 1 Agent
    ub = np.ones(SIMULATION_STEPS) * 20  # Maximal 20 Agenten

    total_waiting_time = 0
    total_profit = 0
    
    model_vars = {}

    # Add the variables to the model
    for i in range(SIMULATION_STEPS):
        model_vars[i] = opt_model.add_variable(domain=poi.VariableDomain.Continuous,
                                               lb=int(lb[i]),
                                               ub=int(ub[i]),
                                               name=f"x{i}")

    # print(model_vars)

    # Minimize the total waiting time
    opt_model.set_objective(objective_function(x0)[0], poi.ObjectiveSense.Minimize)
    opt_model.optimize()

    # Get the optimal solution
    total_waiting_time = opt_model.get_obj_value()


    # Maximize the profit
    opt_model.set_objective(objective_function(x0)[1], poi.ObjectiveSense.Maximize)
    opt_model.optimize()

    # Get the optimal solution
    total_profit = opt_model.get_obj_value()

    print(f"Total waiting time: {total_waiting_time}, Total profit: {total_profit}")

    # Get the optimal solution
    # print([x.get_value() for x in opt_model.get_variables()])

    for k, v in model_vars.items():
        print(f"x{k}: {opt_model.get_variable_attribute(v, poi.VariableAttribute.Value)}")

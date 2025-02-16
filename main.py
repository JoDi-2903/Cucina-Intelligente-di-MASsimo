import pyoptinterface as poi
from pyoptinterface import highs

from mesa_objects.agents.customer_agent import CustomerAgent
from mesa_objects.models.restaurant_model import RestaurantModel
from ml.lstm_model import LSTMModel
from models.config.config import Config


def model_run(restaurant: RestaurantModel, service_agents: int) -> float:
    """
    Objective function to minimize the total waiting time in the restaurant
    :param service_agents: Number of service agents
    """
    # Set the number of service agents and parallel preparation according to the optimization
    Config().service.service_agents = service_agents

    # Run the model with the updated configuration
    while restaurant.running and restaurant.steps < Config().run.step_amount:
        restaurant.step()

    sum_real_waiting_time = restaurant.get_total_waiting_time()
    sum_ideal_waiting_time = restaurant.get_total_ideal_time()

    # Difference is the delay - should always be positive because the idel time does not contain the delay for larger groups. Real >! Ideal
    # The objective is to minimize the delay
    
    # TODO: Add other optimizer for manager. Objective is to maximize the profit or to maximize the rating (restaurant.get_total_rating())
    return sum_real_waiting_time - sum_ideal_waiting_time


if __name__ == '__main__':
    # Create machine learning model
    lstm_model = LSTMModel()
    
    # Create model that solves optimization problems
    opt_model = highs.Model()

    # Create the Mesa Model
    restaurant = RestaurantModel()
    restaurant.lstm_model = lstm_model

    # Define the variables (add 1 to the upper bound to include the upper bound)
    service_agents = list(range(1, 20 + 1))  # There cannot be more than 20 service agents


    # Add the variables to the model
    x = opt_model.add_variables(service_agents,domain=poi.VariableDomain.Continuous, lb=1)

    # Get a list of all possible permutations of the variables for the loop
    # permutations = list(product(service_agents, parallel_preparation, max_customers_per_agent))

    # Variable to store the best objective value and corresponding parameters
    best_obj_value = float('inf')
    best_params = None

    # Iterative optimization over all permutations
    for sa in service_agents:

        # Set the objective function
        opt_model.set_objective(model_run(restaurant, sa), poi.ObjectiveSense.Minimize)

        # Optimize the model
        opt_model.optimize()

        # Check if the current objective value is better than the best one found so far
        if opt_model.get_obj_value() < best_obj_value:
            best_obj_value = opt_model.get_obj_value()
            best_params = sa

        # Print the results
        print(f"\t({sa}) -> Costs: {opt_model.get_obj_value()}")

    """
    # Print the results
    print(f"Total costs: {opt_model.get_obj_value()}")

    for p in permutations:
        print(f"{p}: {opt_model.get_variable_attribute(x[p], poi.VariableAttribute.Value)}")
    """

    # Output the best objective value and corresponding parameters
    print(f"Best objective value: {best_obj_value}")
    print(
        f"Best parameters: Service Agents = {best_params}")

    # TODO: Was macht der Optimizer gerade überhaupt?! Optimizer liefert aktuell immer als Wert 1. Service Agents wird zudem dynamisch über den Manager angepasst

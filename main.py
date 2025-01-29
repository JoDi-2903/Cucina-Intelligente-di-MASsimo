import json
import os
import pyoptinterface as poi
from pyoptinterface import highs
from models import restaurant_model
from agents import customer_agent


def model_run(model: restaurant_model.RestaurantModel, steps):
    """ Run the model for a given number of steps and return the total waiting time """

    while model.running and model.steps < steps:
        model.step()

    # Return the total waiting time (this is the objective function to minimize)
    return model.get_total_waiting_time()


def objective_function(service_agents, parallel_preparation):
    """ Objective function to minimize the total waiting time in the restaurant """

    # Set the number of service agents and parallel preparation according to the optimization
    restaurant.config["num_service_agents"] = service_agents
    restaurant.config["parallel_preparation"] = parallel_preparation

    # Run the model with the updated configuration
    return model_run(restaurant, int(config["Run"]["step_amount"]))


# Load config from config file
with open(os.path.join("data", "config.json"), mode="r", encoding="utf-8") as f:
    config = json.load(f)


# Create the Mesa Model
restaurant = restaurant_model.RestaurantModel(config)

# Create the optimization problem
opt_model = highs.Model()

# Define the variables
# Number of service agents (integer variable between 1 and 20)
service_agents = opt_model.add_variable(domain=poi.VariableDomain.Integer,
                                        lb=1,
                                        ub=20,
                                        name="service_agents")

# Number of parallel preparations (integer variable between 1 and the specified maximum)
parallel_preparation = opt_model.add_variable(domain=poi.VariableDomain.Integer,
                                              lb=1,
                                              ub=int(config["Orders"]["parallel_preparation"]),
                                              name="parallel_preparation")

# Set the objective function
opt_model.set_objective(objective_function(service_agents, parallel_preparation),
                        poi.ObjectiveSense.Minimize)

# Optimize the model
opt_model.optimize()

# Print the results
print(f"Total costs: {opt_model.get_obj_value()}")
print(f"Optimal number of service agents: {opt_model.get_variable_attribute(service_agents, poi.VariableAttribute.Value)}")
print(f"Optimal parallel preparation: {opt_model.get_variable_attribute(parallel_preparation, poi.VariableAttribute.Value)}")
import json
import os
from itertools import product
import pyoptinterface as poi
from pyoptinterface import highs
from models import restaurant_model
from agents import customer_agent


def model_run(config: str, service_agents: int, parallel_preparation: int, max_customers_per_agent: int) -> float:
    """ Objective function to minimize the total waiting time in the restaurant """

    # Create the Mesa Model
    restaurant = restaurant_model.RestaurantModel(config)

    # Set the number of service agents and parallel preparation according to the optimization
    restaurant.config["num_service_agents"] = service_agents
    restaurant.config["parallel_preparation"] = parallel_preparation
    restaurant.config["max_customers_per_agent"] = max_customers_per_agent

    # Run the model with the updated configuration
    while restaurant.running and restaurant.steps < int(config["Run"]["step_amount"]):
        restaurant.step()

    # TODO: Anstatt der Waiting Time die Überschreitung der Gesamtzeit (Zubereitungszeit + Essenszeit als ideal. Im Vergleich zur realen Zeit) berechnen -> Delay reduzieren
    return restaurant.get_total_waiting_time()


# Load config from config file
with open(os.path.join("data", "config.json"), mode="r", encoding="utf-8") as f:
    config = json.load(f)

# Create the optimization problem
opt_model = highs.Model()

# Define the variables (add 1 to the upper bound to include the upper bound)
service_agents = list(range(1,20 + 1))
parallel_preparation = list(range(1, int(config["Orders"]["parallel_preparation"]) + 1))
max_customers_per_agent = list(range(1, int(config["Customers"]["max_customers_per_agent"]) + 1))

# Add the variables to the model
x = opt_model.add_variables(service_agents, parallel_preparation, max_customers_per_agent, domain=poi.VariableDomain.Continuous, lb=1)


# Get a list of all possible permutations of the variables for the loop
permutations = list(product(service_agents, parallel_preparation, max_customers_per_agent))
# TODO: sind max_customers_per_agent und parallel_preparation wirklich die richtigen Variable? Nochmal prüfen und ggf. entfernen

# print(permutations)

# Variable to store the best objective value and corresponding parameters
best_obj_value = float('inf')
best_params = None

# Iterative optimization over all permutations
for sa, pp, cpa in permutations:

    # Set the objective function
    opt_model.set_objective(model_run(config, sa, pp, cpa), poi.ObjectiveSense.Minimize)

    # Optimize the model
    opt_model.optimize()

    # Check if the current objective value is better than the best one found so far
    if opt_model.get_obj_value() < best_obj_value:
        best_obj_value = opt_model.get_obj_value()
        best_params = (sa, pp, cpa)

    # Print the results
    print(f"\t({sa}, {pp}, {cpa}) -> Costs: {opt_model.get_obj_value()}")

"""
# Print the results
print(f"Total costs: {opt_model.get_obj_value()}")

for p in permutations:
    print(f"{p}: {opt_model.get_variable_attribute(x[p], poi.VariableAttribute.Value)}")
"""

# Output the best objective value and corresponding parameters
print(f"Best objective value: {best_obj_value}")
print(f"Best parameters: Service Agents = {best_params[0]}, Parallel Preparation = {best_params[1]}, Max Customers per Agent = {best_params[2]}")

# TODO: Was macht der Optimizer gerade überhaupt?! Wir brauchen mehr Constraints bzw weitere Zielfunktion!
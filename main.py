import json
import os
import pyoptinterface as poi
from pyoptinterface import highs
from models import restaurant_model
from agents import customer_agent


def model_run(model: restaurant_model.RestaurantModel, steps):
    while model.running and model.steps < steps:
        model.step()

    # Return the total waiting time (this is the objective function to minimize)
    return model.get_total_waiting_time()


# Load config from config file
with open(os.path.join("data", "config.json"), mode="r", encoding="utf-8") as f:
    config = json.load(f)


# Create the Mesa Model
restaurant = restaurant_model.RestaurantModel(config)

# Create the optimization problem
opt_model = highs.Model()


# Define the variables for optimization
# Create a variable for each customer's waiting time
waiting_time_vars = {
    agent.unique_id: opt_model.add_variable(
        domain=poi.VariableDomain.Continuous,
        lb=0,  # Waiting time cannot be negative
        name=f"waiting_time_{agent.unique_id}"
    )
    for agent in restaurant.agents_by_type[customer_agent.CustomerAgent]
}

# Define the total waiting time as an affine expression
total_waiting_time_expr = sum(waiting_time_vars[agent.unique_id] \
    for agent in restaurant.agents_by_type[customer_agent.CustomerAgent])

# Constraint: total waiting time must be within the allowed simulation time
opt_model.add_linear_constraint(
    total_waiting_time_expr,
    poi.Leq,
    int(config["Run"]["step_amount"]),
    "max_total_waiting_time"
)


service_agents = opt_model.add_variable(domain=poi.VariableDomain.Integer,
                                        lb=1,
                                        ub=20,
                                        name="service_agents")

parallel_preparation = opt_model.add_variable(domain=poi.VariableDomain.Integer,
                                              lb=1,
                                              ub=int(config["Orders"]["parallel_preparation"]),
                                              name="parallel_preparation")

# Define the cost function (objective function to minimize)
opt_model.set_objective(model_run(restaurant, int(config["Run"]["step_amount"])),
                        poi.ObjectiveSense.Minimize)

# Optimize the model
opt_model.optimize()

print(f"Total costs: {opt_model.get_obj_value()}")

for wt in waiting_time_vars:
    print(f"{wt}: {opt_model.get_variable_attribute(service_agents, poi.VariableAttribute.Value)}, {opt_model.get_variable_attribute(parallel_preparation, poi.VariableAttribute.Value)}")

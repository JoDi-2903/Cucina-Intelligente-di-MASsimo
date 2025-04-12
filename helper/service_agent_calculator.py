from data_structures.config.config import Config

def calculate_minimal_service_agents() -> int:
    """
    Calculate the minimal number of service agents needed in order to make the optimizer work and not to return infeasible.

    :return: The minimal number of service agents needed.
    """

    # Maximum number of customers that fit in the restaurant
    max_customers = Config().restaurant.grid_width * Config().restaurant.grid_height

    # Minimum capacity one service agent can serve per step
    service_agent_min_capacity = Config().service.service_agent_capacity_min

    # Maximum number of time steps one service agent can work in a day
    maximum_slots = (Config().run.full_day_cycle_period // 24) * Config().run.service_agent_max_working_hours


    # Calculate the number of service agents needed to serve all customers in one step
    parallel_service_agents_needed = max_customers // service_agent_min_capacity

    # Since we are calculating the number for one day, we need to multiply the number of service agents needed by the number of time steps per day
    service_agents_time_units_needed = Config().run.full_day_cycle_period * parallel_service_agents_needed

    # One waiter can only work a maximum number of shifts in a day, so we need to divide the number of service agents needed by the maximum number of shifts
    return service_agents_time_units_needed // maximum_slots

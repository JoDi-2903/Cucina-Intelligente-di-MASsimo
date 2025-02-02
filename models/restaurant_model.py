import json

import mesa

from agents import customer_agent, service_agent
from config.config import CONFIG


class RestaurantModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, num_service_agents: int, parallel_preparation: int, max_customers_per_agent: int):
        super().__init__()

        # Read menu from file
        with open(file="data/menu.json", mode="r", encoding="utf8") as file:
            self.menu = json.load(file)

        # Set the number of service agents and parallel preparation according to the optimization
        self.num_service_agents = num_service_agents
        self.parallel_preparation = parallel_preparation
        self.max_customers_per_agent = max_customers_per_agent

        # Initialize agents
        customer_agents = customer_agent.CustomerAgent.create_agents(
            model=self,
            n=CONFIG.customers.customer_agents
        )
        service_agents = service_agent.ServiceAgent.create_agents(
            model=self,
            n=CONFIG.service.service_agents
        )

    def step(self):
        """Advance the model by one step."""
        self.agents.shuffle_do("step")

    def get_total_waiting_time(self):
        """ Compute the total waiting time for all customers in the model """
        return sum(agent.get_waiting_time() for agent in \
                   self.agents_by_type[customer_agent.CustomerAgent])

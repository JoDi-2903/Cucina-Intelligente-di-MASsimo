import json
from agents import customer_agent, service_agent
import mesa

class RestaurantModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, config):
        super().__init__()

        # Read config from configfile
        self.config = config

        # Read menu from file
        with open(file="data/menu.json", mode="r", encoding="utf8") as file:
            self.menu = json.load(file)

        # Initialize agents
        customer_agents = customer_agent.CustomerAgent.create_agents(
            model=self,
            n=int(self.config["Customers"]["customer_agents"])
        )
        service_agents = service_agent.ServiceAgent.create_agents(
            model=self,
            n=int(self.config["Service"]["service_agents"])
        )

    def step(self):
        """Advance the model by one step."""
        self.agents.shuffle_do("step")

    def get_total_waiting_time(self):
        """ Compute the total waiting time for all customers in the model """
        return sum(agent.get_waiting_time() for agent in \
            self.agents_by_type[customer_agent.CustomerAgent])

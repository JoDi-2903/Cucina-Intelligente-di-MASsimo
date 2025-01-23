import configparser
from agents import customer_agent
import mesa

class RestaurantModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self):
        super().__init__()

        # Read config from configfile
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Initialize agents
        agents = customer_agent.CustomerAgent.create_agents(
            model=self,
            config=config,
            n=int(config["Customers"]["customer_agents"])
        )

    def step(self):
        """Advance the model by one step."""
        self.agents.shuffle_do("step")

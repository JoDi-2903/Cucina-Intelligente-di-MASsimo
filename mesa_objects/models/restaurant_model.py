from mesa import Model

from mesa_objects.agents import customer_agent
from mesa_objects.agents.customer_agent import CustomerAgent
from mesa_objects.agents.service_agent import ServiceAgent
from models.config.config import Config
from models.menu import Menu


class RestaurantModel(Model):
    """A model with some number of agents."""

    def __init__(self, num_service_agents: int, parallel_preparation: int, max_customers_per_agent: int):
        super().__init__()

        # Create the menu
        self.menu = Menu()

        # Set the number of service agents and parallel preparation according to the optimization
        self.num_service_agents = num_service_agents
        self.parallel_preparation = parallel_preparation
        self.max_customers_per_agent = max_customers_per_agent

        # Initialize agents
        customer_agents = CustomerAgent.create_agents(
            model=self,
            n=Config().customers.customer_agents
        )
        service_agents = ServiceAgent.create_agents(
            model=self,
            n=Config().service.service_agents
        )

    def step(self):
        """Advance the model by one step."""
        self.agents.shuffle_do("step")

    def get_total_waiting_time(self):
        """ Compute the total waiting time for all customers in the model """
        return sum(agent.get_waiting_time() for agent in \
                   self.agents_by_type[customer_agent.CustomerAgent])

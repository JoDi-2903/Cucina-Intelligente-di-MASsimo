import random
from statistics import fmean
from mesa import Model

from mesa_objects.agents import customer_agent
from mesa_objects.agents.customer_agent import CustomerAgent
from mesa_objects.agents.service_agent import ServiceAgent
from models.config.config import Config
from models.menu import Menu
from models.config.logging_config import restaurant_logger

logger = restaurant_logger

class RestaurantModel(Model):
    """A model with some number of agents."""

    def __init__(self):
        super().__init__()

        # Create the menu
        self.menu = Menu()

        # Initialize agents
        CustomerAgent.create_agents(
            model=self,
            n=Config().customers.max_customer_agents_per_step
        )

        ServiceAgent.create_agents(
            model=self,
            n=Config().service.service_agents
        )

        logger.info(f"Created model with {Config().customers.max_customer_agents_per_step} customer agents and {Config().service.service_agents} service agents")


    def step(self):
        """Advance the model by one step."""
        # spawn new customers
        self.spawn_customers()

        # step all agents
        self.agents.shuffle_do("step")


    def spawn_customers(self):
        """Spawn a new customer agent"""

        # Create more customers the higher the rating
        amount = int(self.get_total_rating_percentage() * Config().customers.max_customer_agents_per_step)

        # Add some randomness to the amount
        amount += random.uniform(-1, 0.3) * amount


        CustomerAgent.create_agents(
            model=self,
            n=int(amount)
        )

        logger.info(f"Spawned {int(amount)} new customer agents. Current rating: {self.get_total_rating():.2f} ({self.get_total_rating_percentage():.2%})")


    # TODO: calculate time only for active agents or for all agents?

    def get_total_waiting_time(self) -> int:
        """ Compute the total waiting time for all customers in the model """
        return sum(agent.get_waiting_time() for agent in \
                   self.agents_by_type[customer_agent.CustomerAgent] \
                   if agent.state != customer_agent.CustomerAgentState.REJECTED)

    def get_total_ideal_time(self) -> int:
        """ Compute the total ideal time for all customers in the model """
        return sum(agent.get_ideal_time() for agent in \
                   self.agents_by_type[customer_agent.CustomerAgent] \
                   if agent.state != customer_agent.CustomerAgentState.REJECTED)

    def get_total_rating(self) -> float | None:
        """ Compute the total rating for all customers in the model """
        return fmean(agent.rating for agent in \
                     self.agents_by_type[customer_agent.CustomerAgent] \
                     if agent.rating is not None)

    def get_total_rating_percentage(self) -> float:
        """ Compute the total rating percentage for all customers in the model """
        return ((self.get_total_rating() - Config().rating.rating_min) /
                (Config().rating.rating_max - Config().rating.rating_min))

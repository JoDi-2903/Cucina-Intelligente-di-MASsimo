from mesa import Agent, Model

from enums.customer_agent_state import CustomerAgentState
from agents import customer_agent, service_agent
from models import restaurant_model
from models.config.config import Config
from models.config.logging_config import manager_logger

logger = manager_logger

class ManagerAgent(Agent):
    def __init__(self, model: Model):
        super().__init__(model)
        self.profit = 0

    def step(self):
        self.control_service_agents()

    def control_service_agents(self):
        """ Control the number of service agents based on the profit """
        # Forecast the visitor count for the next n timesteps after some experience (one completed work day) has been gained
        if self.model.steps > Config().run.full_day_cycle_period:
            forecasted_visitors = self.model.lstm_model.forecast(
                time_series=restaurant_model.RestaurantModel.customers_added_per_step,
                rating_history=restaurant_model.RestaurantModel.rating_over_steps,
                n=3
            )
            # TODO: Implement a more sophisticated algorithm to determine the number of service agents

        # Get the current service agents and the current profit
        current_service_agents = list(self.model.agents_by_type[service_agent.ServiceAgent])
        current_profit = self.calculate_profit()

        # If the profit is lower than the current profit, remove a service agent.
        # The condition for removing a service agent is that there are more than one service agents and that the number of customers is less than the number of service agents times the service agent capacity times 2. Each service agent can temporarily serve twice the amount of customers.
        if current_profit < self.profit:
            if (len(current_service_agents) > 1 and
                len(self.model.agents_by_type[customer_agent.CustomerAgent]) <= 
                (len(current_service_agents) - 1) * Config().service.service_agent_capacity * 2):
                agent_to_remove = self.random.choice(current_service_agents)
                agent_to_remove_customers = agent_to_remove.customer_queue

                logger.info(f"Removing service agent {agent_to_remove.unique_id}. Working agent amount: {len(current_service_agents) - 1}")

                # Remove the agent from the model and the list of service agents
                agent_to_remove.remove()
                current_service_agents.remove(agent_to_remove)

                # Reassign the customers equally to the remaining service agents
                for i, customer in enumerate(agent_to_remove_customers):
                    assigned_agent = current_service_agents[i % len(current_service_agents)]
                    assigned_agent.customer_queue.append(customer)

        # If the profit is higher than the current profit and the overall profit is positive, add a service agent
        elif self.profit > 0:
            logger.info(f"Adding new service agent. Working agent amount: {len(current_service_agents) + 1}")
            service_agent.ServiceAgent.create_agents(model=self.model, n=1)

        self.profit += current_profit

    def calculate_profit(self) -> float:
        """ Profit calculation logic """

        # Calculate the total revenue and payment
        total_revenue = sum(agent.dish.profit * agent.num_people
                            for agent in self.model.agents_by_type[customer_agent.CustomerAgent]
                            if agent.state == CustomerAgentState.FINISHED_EATING)

        total_payment = (Config().service.service_agent_salary_per_tick *
                         len(self.model.agents_by_type[service_agent.ServiceAgent]))

        logger.info(f"Step {self.model.steps}: Revenue: {total_revenue:.2f}, Payment: {total_payment:.2f}, Profit: {total_revenue - total_payment:.2f}. Total profit: {self.profit + total_revenue - total_payment:.2f}")

        return total_revenue - total_payment

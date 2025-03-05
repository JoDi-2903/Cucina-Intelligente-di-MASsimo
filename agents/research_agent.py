import os
from datetime import datetime

import ollama
from mesa import Agent, Model

from agents.customer_agent import CustomerAgent
from agents.manager_agent import ManagerAgent
from agents.service_agent import ServiceAgent
from data_structures.config.config import Config
from enums.customer_agent_state import CustomerAgentState
from main import history


class ResearchAgent(Agent):
    """
    This agent is responsible for calculating statistics and interpreting them using a large language model.
    """

    def __init__(self, model: Model):
        """
        Initialize the research agent with the passed restaurant model and log into the Hugging Face Hub to use the LLM.
        :param model: The restaurant model
        """
        super().__init__(model)

        # If ollama is running, initialize the report folder path
        self.__report_folder_path: str = ""
        if Config().research.is_report_generation_active:
            self.__report_folder_path: str = f"reports/{datetime.now().strftime('%d-%m-%Y_%H-%M-%S-%f')[:-3]}"

    def step(self):
        """
        Update the global history object and write a report if the end of a day is reached.
        """
        self.__update_histories()

        # Interpret the statistics if the agent is logged in and the end of a day is reached
        if Config().research.is_report_generation_active and self.model.steps % Config().run.full_day_cycle_period == 0:
            self.__create_report()

    def __update_histories(self):
        """Update the history lists with the current values."""

        # Store the current step
        history.add_step(self.model.steps)

        # Evaluate the current rating of the restaurant
        history.add_rating(self.model.get_total_rating())

        # Calculate the total time that customers have spent in the restaurant waiting for their food
        history.add_total_time_spent(self.model.get_total_time_spent())
        history.add_total_waiting_time(self.model.get_waiting_time_spent())

        # Update the number of agents
        active_customer_agents = [  # Filter out all customers that are done
            agent for agent in self.model.agents_by_type[CustomerAgent]
            if agent.state != CustomerAgentState.DONE
        ]
        history.add_num_customer_agents(len(active_customer_agents))
        history.add_num_service_agents(len(self.model.agents_by_type[ServiceAgent]))
        history.add_num_active_service_agents(len([a for a in self.model.agents_by_type[ServiceAgent]
                                                   if self.model.steps in a.shift_schedule.keys()
                                                   and a.shift_schedule[self.model.steps] == 1]))
        history.add_num_manager_agents(len(self.model.agents_by_type[ManagerAgent]))
        # history.add_num_agents(
        #     history.num_customer_agents_history[-1] +
        #     history.num_active_service_agents_history[-1] +
        #     history.num_manager_agents_history[-1]
        # )

        # Update the heatmap of the restaurant grid for visualization
        from visualization.restaurant_grid_utils import RestaurantGridUtils  # Avoid circular dependencies
        RestaurantGridUtils.update_grid_heatmap(self.model)

    def __create_report(self):
        """
        Create a report using a LLM model and store it as a Markdown file.
        """
        # Get the number of passed days
        days_count = len(history.rating_history) // Config().run.full_day_cycle_period

        # Get the profit and rating history of the day
        profit_history = history.profit_history[Config().run.full_day_cycle_period * (days_count - 1)
                                                :Config().run.full_day_cycle_period * days_count]
        rating_history = history.rating_history[Config().run.full_day_cycle_period * (days_count - 1)
                                                :Config().run.full_day_cycle_period * days_count]

        # Create the prompt for the report
        prompt = self.__create_prompt(
            profit_history=profit_history,
            highest_profit=max(profit_history),
            highest_profit_time=f"{divmod(profit_history.index(max(profit_history)) * 10, 60)[0]}h {divmod(profit_history.index(max(profit_history)) * 10, 60)[1]}m",
            lowest_profit=min(profit_history),
            lowest_profit_time=f"{divmod(profit_history.index(min(profit_history)) * 10, 60)[0]}h {divmod(profit_history.index(min(profit_history)) * 10, 60)[1]}m",
            rating_history=rating_history,
            peak_rating=max(rating_history),
            peak_rating_time=f"{divmod(rating_history.index(max(rating_history)) * 10, 60)[0]}h {divmod(rating_history.index(max(rating_history)) * 10, 60)[1]}m",
            drop_rating=min(rating_history),
            drop_rating_time=f"{divmod(rating_history.index(min(rating_history)) * 10, 60)[0]}h {divmod(rating_history.index(min(rating_history)) * 10, 60)[1]}m"
        )

        # Generate the report using the LLM model
        report = ollama.chat(
            model=Config().research.llm_model,
            messages=[{"role": "user", "content": prompt}]
        )

        # Store the report as a Markdown file
        os.makedirs(self.__report_folder_path, exist_ok=True)
        with open(f"{self.__report_folder_path}/report_day_{days_count}.md", "w") as file:
            file.write(report["message"]["content"])

    @staticmethod
    def __create_prompt(
            profit_history: list[float],
            highest_profit: float,
            highest_profit_time: str,
            lowest_profit: float,
            lowest_profit_time: str,
            rating_history: list[float],
            peak_rating: float,
            peak_rating_time: str,
            drop_rating: float,
            drop_rating_time: str
    ) -> str:
        """
        Create a prompt for the report with the passed statistics.
        :param profit_history: The profit history of the day.
        :param highest_profit: The highest profit.
        :param highest_profit_time: The time of the highest profit.
        :param lowest_profit: The lowest profit.
        :param lowest_profit_time: The time of the lowest profit.
        :param rating_history: The rating history of the day.
        :param peak_rating: The peak rating.
        :param peak_rating_time: The time of the peak rating.
        :param drop_rating: The dropped rating.
        :param drop_rating_time: The time of the dropped rating.
        """
        return f"""
You are a data analyst reviewing statistical changes in a restaurant's performance over time. Below is a dataset containing key performance metrics in 10-minute intervals:

- **Profit (€):** Total profit generated during each interval.
- **Customer Rating (1-5 Stars):** Average customer rating collected via a feedback system.

### **Summary of Key Changes:**
- **Profit:**
  - Recorded profit throughout the day in 10-minute intervals: {profit_history}
  - Highest recorded profit: {highest_profit}€ at {highest_profit_time}.
  - Lowest recorded profit: {lowest_profit}€ at {lowest_profit_time}.

- **Customer Rating:**
  - Recorded rating throughout the day in 10-minute intervals: {rating_history}
  - Peak rating of {peak_rating} at {peak_rating_time}.
  - Sharp drop to {drop_rating} around {drop_rating_time}.
        """

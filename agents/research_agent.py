from huggingface_hub import login
from mesa import Agent, Model
from transformers import pipeline

from agents.customer_agent import CustomerAgent
from agents.manager_agent import ManagerAgent
from agents.service_agent import ServiceAgent
from data_structures.config.config import Config
from data_structures.config.logging_config import research_logger
from enums.customer_agent_state import CustomerAgentState
from main import history

logger = research_logger


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
        self.__logged_in: bool = False

        # Try to log into the Hugging Face Hub
        if Config().research.huggingface_token != "" and Config().research.llm_model_id != "":
            try:
                login(token=Config().research.huggingface_token)
                self.__logged_in: bool = True
            except Exception as e:
                logger.error(f"Could not log into Hugging Face Hub: {e}")

    def step(self):
        """
        Update the global history object and write a report if the end of a day is reached.
        """
        self.__update_histories()

        # Interpret the statistics if the agent is logged in and the end of a day is reached
        if self.__logged_in and self.model.steps % Config().run.full_day_cycle_period == 0:
            self.__interpret_statistics()

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
                                                   and a.shift_schedule[self.model.steps] is True]))
        history.add_num_manager_agents(len(self.model.agents_by_type[ManagerAgent]))
        # history.add_num_agents(
        #     history.num_customer_agents_history[-1] +
        #     history.num_active_service_agents_history[-1] +
        #     history.num_manager_agents_history[-1]
        # )

        # Update the heatmap of the restaurant grid for visualization
        from visualization.restaurant_grid_utils import RestaurantGridUtils  # Avoid circular dependencies
        RestaurantGridUtils.update_grid_heatmap(self.model.model)

    def __interpret_statistics(self):
        """
        Interpret the statistics using the LLM model and log the results.
        """
        # Initialize the generator
        generator = pipeline("text-generation", model="openai-community/gpt2")

        # Interpret the profit change
        profit_yesterday, profit_today = self.__get_yesterday_and_today_values(history.profit_history)
        profit_prompt = f"The restaurant's profit is {profit_today}€ and yesterday it was {profit_yesterday}€. So it has grown"
        profit_result = generator(profit_prompt, max_length=1024, num_return_sequences=1, truncation=True)
        logger.info(profit_result[0]['generated_text'])

        # Interpret the rating change
        rating_yesterday, rating_today = self.__get_yesterday_and_today_values(history.rating_history)
        rating_prompt = f"The restaurant's rating is {rating_today} stars and yesterday it was {rating_yesterday} stars. So it has grown"
        rating_result = generator(rating_prompt, max_length=1024, num_return_sequences=1, truncation=True)
        logger.info(rating_result[0]['generated_text'])

        # Interpret the time spent change
        time_spent_yesterday, time_spent_today = self.__get_yesterday_and_today_values(history.total_time_spent_history)
        time_spent_prompt = f"The restaurant's rating is {time_spent_today} stars and yesterday it was {time_spent_yesterday} stars. So it has grown"
        time_spent_result = generator(time_spent_prompt, max_length=1024, num_return_sequences=1, truncation=True)
        logger.info(time_spent_result[0]['generated_text'])

    @staticmethod
    def __get_yesterday_and_today_values(history_array: list[int or float]) -> tuple[int or float, int or float]:
        """
        Get the total values of yesterday and today from the passed history array.
        :param history_array: The history array to get the values from.
        :return: The values of yesterday and today.
        """
        # Get the days that have passed
        passed_days_count = len(history_array) // Config().run.full_day_cycle_period

        # Sum up the values from yesterday to today
        today_values = history_array[
                       Config().run.full_day_cycle_period * (passed_days_count - 1)
                       :Config().run.full_day_cycle_period * passed_days_count
                       ]
        today_value = sum(value for value in today_values)

        # Sum up the values from the day before yesterday to yesterday
        if passed_days_count < 2:
            yesterday_value = 0
        else:
            yesterdays_values = history_array[
                                Config().run.full_day_cycle_period * (passed_days_count - 2)
                                :Config().run.full_day_cycle_period * (passed_days_count - 1)
                                ]
            yesterday_value = sum(value for value in yesterdays_values)

        return yesterday_value, today_value

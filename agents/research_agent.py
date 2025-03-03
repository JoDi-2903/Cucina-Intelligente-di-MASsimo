import torch
from huggingface_hub import login
from mesa import Agent, Model
from transformers import AutoTokenizer, AutoModelForCausalLM, GPT2LMHeadModel, GPT2TokenizerFast, pipeline

from agents.customer_agent import CustomerAgent
from agents.manager_agent import ManagerAgent
from agents.service_agent import ServiceAgent
from data_structures.config.config import Config
from enums.customer_agent_state import CustomerAgentState
from main import history


class ResearchAgent(Agent):
    """
    This agent is responsible for calculating statistics and writing reports.
    """

    def __init__(self, model: Model):
        """
        Initialization method for the research agent.
        :param model: The restaurant model
        """
        super().__init__(model)

        # Check if the llama model path leads to a valid model
        if Config().research.huggingface_token != "" and Config().research.llm_model_id != "":
            try:
                # Login to the Hugging Face Hub
                login(token=Config().research.huggingface_token)

                # Use MPS if available, otherwise GPU, otherwise CPU
                if torch.backends.mps.is_available():
                    device: str = "mps"
                elif torch.cuda.is_available():
                    device: str = "cuda"
                else:
                    device: str = "cpu"

                # Initialize the model and tokenizer
                self.__llm_model: GPT2LMHeadModel or None = AutoModelForCausalLM.from_pretrained(
                    Config().research.llm_model_id,
                    device_map={"": device}
                )
                self.__llm_tokenizer: GPT2TokenizerFast or None = AutoTokenizer.from_pretrained(Config().research.llm_model_id)

            except Exception as e:
                self.__llm_model: GPT2LMHeadModel or None = None
                self.__llm_tokenizer: GPT2TokenizerFast or None = None
                from models.restaurant_model import logger
                logger.error(f"Could not load the LLM model: {e}")

    def step(self):
        """
        Update the global history object and write a report if the end of a day is reached.
        """
        self.__update_histories()

        # Write a report if the end of a day is reached
        if self.__llm_model is not None and self.__llm_tokenizer is not None and self.model.steps % Config().run.full_day_cycle_period == 0:
            self.__write_report()

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

    def __write_report(self):
        """
        Write a report with the current statistics.
        """
        generator = pipeline("text-generation", model="openai-community/gpt2")
        result = generator(prompt, pad_token_id=50256, num_return_sequences=1)

import os


class ResearchSettings:
    """
    Class to store the research settings.
    """

    def __init__(self, config: dict[str] = None):
        """
        Initialize the research object with the passed configuration or default values.
        """
        if config is not None:
            # The grid width and height are used to visualize the restaurant in a grid and determine the maximum capacity of customer agents in the restaurant.
            self.__huggingface_token = config["huggingface_token"]
            self.__llm_model_id = "openai-community/gpt2"
        else:
            os.environ["HUGGINGFACE_TOKEN"] = ''
            self.__llama_model_path: str = ""

    @property
    def huggingface_token(self) -> str:
        return self.__huggingface_token

    @property
    def llm_model_id(self) -> str:
        return self.__llm_model_id

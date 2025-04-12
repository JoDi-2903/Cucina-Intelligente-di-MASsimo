import requests


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
            self.__llm_model = config["llm_model"]
            self.__is_report_generation_active: bool = self.__is_ollama_running()
        else:
            self.__llm_model: str = ""
            self.__is_report_generation_active: bool = False

    @staticmethod
    def __is_ollama_running() -> bool:
        """
        Check if the ollama server is running.
        :return: True if the server is running, False otherwise
        """
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    @property
    def llm_model(self) -> str:
        return self.__llm_model

    @property
    def is_report_generation_active(self) -> bool:
        return self.__is_report_generation_active

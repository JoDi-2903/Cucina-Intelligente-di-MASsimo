from data_structures.config.config import Config


class History:
    """A class to store the history of the simulation which will be visualized on a dashboard."""

    def __init__(self):
        # History of steps
        self.__steps_history: list[int] = []

        # History of rating and profit
        self.__rating_history: list[float] = [Config().rating.rating_default]
        self.__profit_history: list[float] = []

        # History of time spent by a customer
        self.__total_time_spent_history: list[int] = []
        self.__total_waiting_time_history: list[int] = []

        # History of agent counts
        self.__num_agents_history: list[int] = []
        self.__num_customer_agents_history: list[int] = []
        self.__num_service_agents_history: list[int] = []
        self.__num_active_service_agents_history: list[int] = []
        self.__num_manager_agents_history: list[int] = []
        self.__customers_added_history: list[int] = [Config().customers.max_new_customer_agents_per_step]
        self.__predicted_customers_agents_growth_history: list[int] = []

        # Current heatmap image of the restaurant grid (used for visualization)
        self.restaurant_grid_heatmap_image: str = ""

    def add_step(self, step: int):
        self.__steps_history.append(step)

    def add_rating(self, rating: float):
        self.__rating_history.append(rating)

    def add_profit(self, profit: float):
        self.__profit_history.append(profit)

    def add_customers_added(self, customers_added: int):
        self.__customers_added_history.append(customers_added)

    def add_predicted_customer_agents_growth(self, predicted_customer_growth: list[int]):
        self.__predicted_customers_agents_growth_history.extend(predicted_customer_growth)

    def add_total_time_spent(self, total_time_spent: int):
        self.__total_time_spent_history.append(total_time_spent)

    def add_total_waiting_time(self, total_waiting_time: int):
        self.__total_waiting_time_history.append(total_waiting_time)

    def add_num_agents(self, num_agents: int):
        self.__num_agents_history.append(num_agents)

    def add_num_customer_agents(self, num_customer_agents: int):
        self.__num_customer_agents_history.append(num_customer_agents)

    def add_num_service_agents(self, num_service_agents: int):
        self.__num_service_agents_history.append(num_service_agents)

    def add_num_active_service_agents(self, num_active_service_agents: int):
        self.__num_active_service_agents_history.append(num_active_service_agents)

    def add_num_manager_agents(self, num_manager_agents: int):
        self.__num_manager_agents_history.append(num_manager_agents)

    @property
    def steps_history(self) -> list[int]:
        return self.__steps_history

    @property
    def rating_history(self) -> list[float]:
        return self.__rating_history

    @property
    def profit_history(self) -> list[float]:
        return self.__profit_history

    @property
    def customers_added_history(self) -> list[int]:
        return self.__customers_added_history

    @property
    def predicted_customer_growth_history(self) -> list[int]:
        return self.__predicted_customers_agents_growth_history

    @property
    def total_time_spent_history(self) -> list[int]:
        return self.__total_time_spent_history

    @property
    def total_waiting_time_history(self) -> list[int]:
        return self.__total_waiting_time_history

    @property
    def num_agents_history(self) -> list[int]:
        return self.__num_agents_history

    @property
    def num_customer_agents_history(self) -> list[int]:
        return self.__num_customer_agents_history

    @property
    def num_service_agents_history(self) -> list[int]:
        return self.__num_service_agents_history

    @property
    def num_active_service_agents_history(self) -> list[int]:
        return self.__num_active_service_agents_history

    @property
    def num_manager_agents_history(self) -> list[int]:
        return self.__num_manager_agents_history

from enum import Enum


class CustomerAgentState(Enum):
    """State for the CustomerAgent class"""
    WAIT_FOR_SERVICE_AGENT = 0  # gets selected by ServiceAgent
    WAITING_FOR_FOOD = 1
    EATING = 2
    FINISHED_EATING = 3  # rating accordingly + agent set to done
    REJECTED = 4  # worst rating + agent set to done
    DONE = 5

    def __str__(self):
        return self.name

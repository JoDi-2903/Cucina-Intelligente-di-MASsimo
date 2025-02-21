from visualization.messages.agents_message import AgentsMessage
from visualization.messages.profit_message import ProfitMessage
from visualization.messages.time_spent_message import TimeSpentMessage


class DashboardMessage:
    def __init__(
            self,
            step: int,
            agent_message: AgentsMessage,
            profit_message: ProfitMessage,
            time_spent_message: TimeSpentMessage
    ):
        self.step = step
        self.agent_message = agent_message
        self.profit_message = profit_message
        self.time_spent_message = time_spent_message

    def to_dict(self):
        return {
            "step": self.step,
            "agent_message": self.agent_message.to_dict(),
            "profit_message": self.profit_message.to_dict(),
            "time_spent_message": self.time_spent_message.to_dict()
        }

class AgentsMessage:
    def __init__(self, num_agents: int, num_customer_agents: int, num_service_agents: int,
                 num_manager_agents: int):
        self.num_agents = num_agents
        self.num_customer_agents = num_customer_agents
        self.num_service_agents = num_service_agents
        self.num_manager_agents = num_manager_agents

    def to_dict(self):
        return {
            "num_agents": self.num_agents,
            "num_customer_agents": self.num_customer_agents,
            "num_service_agents": self.num_service_agents,
            "num_manager_agents": self.num_manager_agents
        }

from agents import customer_agent
import mesa

class ServiceAgent(mesa.Agent):
    """An agent that represents the service in the restaurant"""
    def __init__(self, model: mesa.Model):
        super().__init__(model)

    def step(self):        
        # Add waiting customers to queue
        for customer in filter(lambda a:
                               a.state == customer_agent.CustomerAgentState.WAIT_FOR_SERVICE_AGENT,
                               self.model.agents_by_type[customer_agent.CustomerAgent]):

            # If overall time for selected food exceeds the time left, reject the customer
            if customer.menu_item["preparationTime"] + customer.menu_item["eatingTime"] > customer.time_left:
                customer.state = customer_agent.CustomerAgentState.REJECTED
            # Else add customer to the queue
            else:
                self.model.customer_queue.append(customer)
                customer.state = customer_agent.CustomerAgentState.WAITING_FOR_FOOD

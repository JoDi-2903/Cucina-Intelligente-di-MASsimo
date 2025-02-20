import numpy as np
from mesa import Agent, Model

from agents import service_agent, customer_agent
from agents.service_agent import ServiceAgent
from enums.customer_agent_state import CustomerAgentState
from models import restaurant_model
from models.config.config import Config
from models.config.logging_config import manager_logger

logger = manager_logger


class ManagerAgent(Agent):
    def __init__(self, model: Model):
        super().__init__(model)
        self.profit = 0

    def step(self):
        """
        Control the number of service agents and update the profit of the restaurant.
        """
        # If the retrain interval is reached, update the number of service agents
        if self.model.steps > Config().run.full_day_cycle_period:
            self.__update_service_agents()

        # Get the current service agents and the current profit
        self.profit = self.calculate_profit()

    def calculate_profit(self) -> float:
        """
        Calculate the profit of the restaurant based on the total revenue and total payment.
        """
        # Calculate the total revenue and payment
        total_revenue = sum(
            customer_agent.dish.profit * customer_agent.num_people
            for customer_agent in self.model.agents_by_type[customer_agent.CustomerAgent]
            if customer_agent.state == CustomerAgentState.FINISHED_EATING
        )

        total_payment = (Config().service.service_agent_salary_per_tick *
                         len(self.model.agents_by_type[service_agent.ServiceAgent]))

        logger.info(
            "Step %d: Revenue: %.2f, Payment: %.2f, Profit: %.2f. Total profit: %.2f",
            self.model.steps, total_revenue, total_payment, total_revenue - total_payment, self.profit + total_revenue - total_payment
        )

        return total_revenue - total_payment

    def __update_service_agents(self):
        """
        Predict the visitor count and update the number of service agents based on the prediction.
        """
        # Forecast the visitor counts for the next n iterations
        predicted_visitor_counts = self.model.lstm_model.forecast(
            time_series=restaurant_model.RestaurantModel.customers_added_per_step,
            rating_history=restaurant_model.RestaurantModel.rating_over_steps,
            n=Config().run.retrain_interval // 2  # Forecast the next n time steps
        )

        # Calculate the average predicted visitor count
        predicted_visitor_count = np.mean(predicted_visitor_counts)

        # Calculate the number of service agents based on the predicted visitor count
        num_service_agents = max(1, predicted_visitor_count // Config().service.service_agent_capacity)

        # Add or remove service agents based on the predicted visitor count
        current_service_agents = len(self.model.agents_by_type[ServiceAgent])

        # TODO JD: Optimierung Schichtplanung: Inhalt dieser Funktion durch pyoptinterface optimieren
            # evtl. "Kündigungsfrist" oder "Anfahrtszeit" für Service Agents

        # Entscheidungsvariablen:
        # service_agent_daily_working_hours: upper bound (Arbeitsschutz), lower bound
        # parallel_preparation: je mehr gleichzeitig, desto teurer
            # Kosten pro Tick: service_agent_salary_per_tick * parallel_preparation
        # evtl. Qualityfaktor für teureres Essen -> Rating & Profit
        # evtl. Optimierungsmodell entscheidet gewichtet über die zu verwendende Zielfunktion

        # Zielfunktionen:
            # 1. Maximierung des Profits: Profit für die letzten full_day_cycle Steps ablegen
            # 2. Maximierung der Zufriedenheit: restaurant.rating_over_steps
        
        # Constraints:
            # Maximale Anzahl an Service Agents
            # Maximale Anzahl an Kunden pro Service Agent -> existiert schon
            # Maximale Anzahl an Arbeitsstunden pro Service Agent

        # Optimierungsmodell direkt im Manager Agent implementieren und nach full_day_cycle Steps ausführen
        # Das Ergebnis der Optimierung wird dann global gesetzt

        # Wir haben einen festen Mitarbeiterstamm. Diese Mitarbeiter haben Arbeitszeiten, die sie nicht überschreiten dürfen. Es gibt Mitarbeiter mit weniger Arbeitszeit und Mitarbeiter mit mehr Arbeitszeit. Das Problem ist jetzt, die Mitarbeiter für den nächsten Tag so einzuteilen, dass der Profit maximiert wird. Die Mitarbeiter werden im Laufe des Tages nicht verändert. Der Faktor parallel_preparation kann unterschiedlich je Mitarbeiter sein; je höher, desto höher das Gehalt des Mitarbeiters.

        # Manager speichert jeden Schritt den aktuellen Profit und legt ihn im Restaurant ab


        if num_service_agents > current_service_agents:
            service_agent.ServiceAgent.create_agents(
                model=self.model,
                n=(num_service_agents - current_service_agents)
            )
            logger.info("Added new service agent. Working agent amount: %d", current_service_agents + 1)
        elif num_service_agents < current_service_agents:
            remove_amount = current_service_agents - num_service_agents

            # Ensure that at least one service agent remains
            if remove_amount > num_service_agents:
                remove_amount -= 1

            for _ in range(remove_amount):
                self.__remove_service_agent()

    def __remove_service_agent(self):
        """
        Remove a services agent and reassign the customers to the customer queue of the remaining service agents.
        """
        # Pick a random service agent to remove and get the customers from the agent to reassign them
        agent_to_remove = self.random.choice(list(self.model.agents_by_type[ServiceAgent]))
        remaining_customers = agent_to_remove.customer_queue

        logger.info(
            "Removing service agent %d. Working agent amount: %d",
            agent_to_remove.unique_id,
            len(self.model.agents_by_type[ServiceAgent]) - 1
        )

        # Remove the agent from the model
        agent_to_remove.remove()

        # Reassign the customers equally to the remaining service agents
        for i, customer in enumerate(remaining_customers):
            assigned_agent = self.model.agents_by_type[ServiceAgent][i % len(self.model.agents_by_type[ServiceAgent])]
            assigned_agent.customer_queue.append(customer)

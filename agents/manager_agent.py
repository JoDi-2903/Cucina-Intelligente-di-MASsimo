import numpy as np
from mesa import Agent, Model

from agents import service_agent
from agents.customer_agent import CustomerAgent
from agents.service_agent import ServiceAgent
from enums.customer_agent_state import CustomerAgentState
from models import restaurant_model
from models.config.config import Config
from models.config.logging_config import manager_logger

logger = manager_logger


class ManagerAgent(Agent):
    def __init__(self, model: Model):
        super().__init__(model)

    def step(self):
        """
        Make tweaks to the restaurant's operations to optimize the manager's goal.
        """
        # Calculate and save the current profit over each step
        self.model.profit_over_steps[self.model.steps] = self.calculate_profit()

        # If the end of the working day is reached, run optimization model 
        if self.model.steps % Config().run.full_day_cycle_period == 0:
            self._optimize_restaurant_operations()

    def calculate_profit(self) -> float:
        """
        Calculate the profit of the restaurant based on the total revenue and total payment.
        """
        # Calculate the total revenue and payment
        total_revenue = sum(
            customer_agent.dish.profit * customer_agent.num_people
            for customer_agent in self.model.agents_by_type[CustomerAgent]
            if customer_agent.state == CustomerAgentState.FINISHED_EATING
        )

        total_payment = (Config().service.service_agent_salary_per_tick *
                         len(self.model.agents_by_type[service_agent.ServiceAgent]))

        logger.info(
            "Step %d: Revenue: %.2f, Payment: %.2f, Profit: %.2f. Total profit: %.2f",
            self.model.steps, total_revenue, total_payment, total_revenue - total_payment, self.profit + total_revenue - total_payment
        )

        return total_revenue - total_payment

    def _optimize_restaurant_operations(self):
        """
        Create a new shift plan with the optimization model for the next working day.

        Problem description:
            We have a dedicated team of employees and a series of constraints derived mainly from the Occupational Health and Safety Act. 
            Some employees are scheduled to work fewer hours and shifts, while others work more. It does not have to be balanced or fair, 
            but must contribute to the target function in the best possible way. The challenge is to assign employees for the following day 
            in a way that maximizes overall profit. Employees will not be reassigned or replaced during the course of the day. Additionally, 
            each employee has a unique "parallel_preparation" factor, which represents their efficiency or skill level—the higher this factor, 
            the higher the employee's salary.
        """
        # Forecast the visitor counts for the next work day
        predicted_visitor_counts = self.model.lstm_model.forecast(
            time_series=restaurant_model.RestaurantModel.customers_added_per_step,
            rating_history=restaurant_model.RestaurantModel.rating_over_steps,
            n=Config().run.full_day_cycle_period
        )

        # TODO JD: Optimierung Schichtplanung: Inhalt dieser Funktion durch pyoptinterface optimieren
        # Optimierungsmodell direkt im Manager Agent implementieren und nach full_day_cycle Steps ausführen
        # Das Ergebnis der Optimierung wird dann global gesetzt und die Service Agents entsprechend eingeteilt


        # Entscheidungsvariablen:
        # predicted_visitor_counts: Vorhersage der Besucherzahlen pro step für den nächsten Arbeitstag; Dictionary mit step als Key und Besucherzahl als Value
        # available_service_agents: Liste mit allen Service Agents, die am nächsten Arbeitstag arbeiten können; 
        #   für jeden Service Agent ein Dictionary mit den folgenden Keys (die wiederrum Entscheidungsvariablen sind):
        #       - salary_per_tick: Gehalt pro Tick
        #       - parallel_customer_operation: Anzahl der Kunden, die ein Service Agent gleichzeitig bedienen kann
        # service_agent_shift_schedule: Schichtplan eines Service Agents am geplanten Tag; 1 = arbeiten, 0 = frei; Datentyp als Liste mit 24 Einträgen (für 24 Stunden; 0-23 Uhr);
        #   soll ein Agent aus dem Mitarbeiterpool arbeiten, wird ein Eintrag in der Liste auf 1 gesetzt, ansonsten auf 0 (es muss ja nicht jeder eingesetzt werden)
        # service_agent_working_hours_count: Arbeitsstunden in steps eines Service Agents am geplanten Tag (ergibt sich aus service_agent_shift_schedule)
        # service_agent_working_shifts_count: Anzahl der Schichten, die ein Service Agent am geplanten Tag (ergibt sich aus service_agent_shift_schedule)
        # service_agent_count: Anzahl der Service Agents, die am nächsten Arbeitstag arbeiten sollen (ergibt sich aus service_agent_shift_schedule)

        # Zielfunktionen:
            # 1. Maximierung des Profits: self.profit_over_steps
            # 2. Maximierung der Zufriedenheit: restaurant.rating_over_steps
            # Optimierungsmodell entscheidet gewichtet über die zu verwendende Zielfunktion (Profit ODER Zufriedenheit)
        
        # Constraints:
            # Maximale Anzahl an Service Agents, die Zeitgleich arbeiten können
            # Maximale Anzahl an Kunden, die ein Service Agent pro step bedienen kann (abhängig von Fähigkeiten eines Service Agents)
            # Service Agents bekommen pro step ein Gehalt, dass von ihrer Fähigkeit abhängt (salary_per_tick)
            # Service Agents bekommen ein höheres Gehalt, wenn sie eine höhere Fähigkeit besitzen und mehr Kunden gleichzeitig bedienen können (parallel_customer_operation)
            # Eine Schicht muss mindestens 6 steps (1 Stunde) dauern
            # Ein Service Agent kann maximal 3 Schichten pro Tag arbeiten
            # Ein Service Agent kann maximal 36 steps (6 Stunden) am Stück arbeiten, länger darf eine Schicht nicht sein
            # Ein Service Agent darf maximal 48 steps (8 Stunden) pro Tag arbeiten (Arbeitsschutzgesetz)
            # Zwischen zwei Schichten eines Service Agents muss mindestens 6 steps (1 Stunde) Pause liegen
            # Schichten können nur zu vollen Stunden beginnen (alle 6 Steps) beginnen
            # Schichten können nur zu vollen Stunden enden (alle 6 Steps) enden

        ## Zusatzideen:
        ## parallel_preparation: je mehr Gerichte gleichzeitig zubereitet werden können sollen, desto teurer
        # evtl. Qualityfaktor für teureres Essen -> Rating & Profit



# OLD HEURISTIC LOGIC ------------------------------------------------------------------------------
#        # Calculate the average predicted visitor count
#        predicted_visitor_count = np.mean(predicted_visitor_counts)
#
#        # Calculate the number of service agents based on the predicted visitor count
#        num_service_agents = max(1, predicted_visitor_count // Config().service.service_agent_capacity)
#
#        # Add or remove service agents based on the predicted visitor count
#        current_service_agents = len(self.model.agents_by_type[ServiceAgent])
#
#        if num_service_agents > current_service_agents:
#            service_agent.ServiceAgent.create_agents(
#                model=self.model,
#                n=(num_service_agents - current_service_agents)
#            )
#            logger.info("Added new service agent. Working agent amount: %d", current_service_agents + 1)
#        elif num_service_agents < current_service_agents:
#            remove_amount = current_service_agents - num_service_agents
#
#            # Ensure that at least one service agent remains
#            if remove_amount > num_service_agents:
#                remove_amount -= 1
#
#            for _ in range(remove_amount):
#                self.__remove_service_agent()
#
#    def __remove_service_agent(self):
#        """
#        Remove a services agent and reassign the customers to the customer queue of the remaining service agents.
#        """
#        # Pick a random service agent to remove and get the customers from the agent to reassign them
#        agent_to_remove = self.random.choice(list(self.model.agents_by_type[ServiceAgent]))
#        remaining_customers = agent_to_remove.customer_queue
#
#        logger.info(
#            "Removing service agent %d. Working agent amount: %d",
#            agent_to_remove.unique_id,
#            len(self.model.agents_by_type[ServiceAgent]) - 1
#        )
#
#        # Remove the agent from the model
#        agent_to_remove.remove()
#
#        # Reassign the customers equally to the remaining service agents
#        for i, customer in enumerate(remaining_customers):
#            assigned_agent = self.model.agents_by_type[ServiceAgent][i % len(self.model.agents_by_type[ServiceAgent])]
#            assigned_agent.customer_queue.append(customer)

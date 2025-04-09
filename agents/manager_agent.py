import numpy as np
import pyoptinterface as poi
from mesa import Agent, Model
from pyoptinterface import highs

from agents import service_agent
from agents.customer_agent import CustomerAgent
from agents.service_agent import ServiceAgent
from data_structures.config.config import Config
from data_structures.config.logging_config import manager_logger
from enums.customer_agent_state import CustomerAgentState
from main import history

logger = manager_logger


class ManagerAgent(Agent):
    def __init__(self, model: Model):
        super().__init__(model)

    def step(self):
        """
        Make tweaks to the restaurant's operations to optimize the manager's goal.
        """
        # Update the employee pool of service agents
        if (
                self.model.steps % (Config().run.full_day_cycle_period * 5) == 0
                or self.model.steps == 1
        ):  # Update every 5 full day cycles
            self.update_service_agent_employee_pool()

        # Calculate and save the current profit over each step
        history.add_profit(self.calculate_profit())

        # If the end of the working day is reached, run optimization model
        if self.model.steps % Config().run.full_day_cycle_period == 0 or self.model.steps == 1:
            self._optimize_restaurant_operations()

    def optimize_shift_schedule(
            self, agents: list, predicted_visitors: list[int]
    ) -> tuple[dict, float]:
        """
        Optimize the shift schedule for the service agents to maximize profit.
        :param agents: List of service agents
        :param predicted_visitors: Predicted number of visitors for each time slot
        :return: agent schedules (dict[agent, list(works_at_step_binary)]) and optimal objective value (total cost)
        """
        # Time parameters
        n_slots = len(
            predicted_visitors
        )  # e.g., 144 time slots for a 24-hour day (10 minutes each)
        slots_per_hour = 6  # 6 slots per hour (10 minutes each)
        n_hours = 24
        shift_duration_hours = 6  # Each shift lasts 6 hours
        shift_duration_slots = shift_duration_hours * slots_per_hour  # e.g. 36 slots per shift
        n_shifts = n_hours // shift_duration_hours  # 4 shifts per day
        shifts = [
            list(range(s * shift_duration_slots, (s + 1) * shift_duration_slots))
            for s in range(n_shifts)
        ]

        # Parameters for each agent
        max_working_slots = 48  # Maximum working time slots per agent per day
        max_shifts = 3  # Maximum number of shifts per agent per day

        # Create an optimization model using Highs
        model = highs.Model()

        # Decision variables dictionaries:
        # x_vars[(agent, t)] = binary: 1 if agent works at time slot t, 0 otherwise.
        # y_vars[(agent, s)] = binary: 1 if agent is assigned to shift s, 0 otherwise.
        x_vars = {}
        y_vars = {}

        for agent in agents:
            for t in range(n_slots):
                var_name = f"x_{agent.unique_id}_{t}"
                # Create a binary variable by using Integer domain with bounds 0 and 1
                x_vars[(agent, t)] = model.add_variable(
                    lb=0, ub=1, domain=poi.VariableDomain.Integer, name=var_name
                )
            for s in range(n_shifts):
                var_name = f"y_{agent.unique_id}_shift_{s}"
                y_vars[(agent, s)] = model.add_variable(
                    lb=0, ub=1, domain=poi.VariableDomain.Integer, name=var_name
                )

        # Objective: Minimize total salary cost over all time slots
        obj_expr = 0
        for agent in agents:
            for t in range(n_slots):
                obj_expr += agent.salary_per_tick * x_vars[(agent, t)]
        model.set_objective(obj_expr, poi.ObjectiveSense.Minimize)

        # Constraint 1: Demand fulfillment for each time slot.
        # The sum of customer capacities of active agents must meet or exceed predicted visitors.
        for t in range(n_slots):
            cons_expr = 0
            for agent in agents:
                cons_expr += agent.customer_capacity * x_vars[(agent, t)]
            model.add_linear_constraint(cons_expr, poi.Geq, predicted_visitors[t])

        # Constraint 2: Maximum number of working time slots per agent.
        # ToDo: Entweder max. Arbeitswerte anpassen oder Schichten kürzer unterglieder (Sub-Mengen und nicht nur 6h-Schichten); aktuell mit max. 8h nur eine Schicht
        for agent in agents:
            cons_expr = 0
            for t in range(n_slots):
                cons_expr += x_vars[(agent, t)]
            model.add_linear_constraint(cons_expr, poi.Leq, max_working_slots)

        # Constraint 3: Shift consistency.
        # If an agent is assigned to a shift y_{a,s} == 1, then they must work every time slot x_{a,t} == 1 in that shift.
        # Enforced for each t in the shift s by: 
            # c1: y_{a,s} - x_{a,t} <= 0 AND
            # c2: x_{a,t} - y_{a,s} <= 0
            # s t  desired  c1  c2  c1 & c2
            # 0 0  1        1   1   1
            # 0 1  0        1   0   0
            # 1 0  0        0   1   0
            # 1 1  1        1   1   1

        # c1: s-t <= 0
        # c2: t-s <= 0 
        for agent in agents:
            for s in range(n_shifts):
                for t in shifts[s]:
                    model.add_linear_constraint(y_vars[(agent, s)] - x_vars[(agent, t)], poi.Leq, 0)
                    model.add_linear_constraint(x_vars[(agent, t)] - y_vars[(agent, s)], poi.Leq, 0)

        # Constraint 4: Maximum number of shifts per agent.
        for agent in agents:
            cons_expr = 0
            for s in range(n_shifts):
                cons_expr += y_vars[(agent, s)]
            model.add_linear_constraint(cons_expr, poi.Leq, max_shifts)

        # Solve the optimization model using Highs
        model.optimize()

        if model.get_model_attribute(poi.ModelAttribute.TerminationStatus) != poi.TerminationStatusCode.OPTIMAL:
            raise Exception(
                f"Optimization failed with status: {model.get_model_attribute(poi.ModelAttribute.TerminationStatus)}"
            )

        # Retrieve the schedule for each agent across all time slots.
        agent_schedules = {}
        for agent in agents:
            schedule = []
            for t in range(n_slots):
                # The model returns values close to 0 or 1.
                schedule.append(model.get_value(x_vars[(agent, t)]))
            agent_schedules[agent] = schedule

        optimal_objective = model.get_obj_value()

        # Print the optimal objective and the schedule for each agent
        print(f"Optimal objective: {optimal_objective}")
        # for a in agents:
        #     print(f"Agent {a.unique_id}".center(20, "-"))
        #     for t in range(n_slots):
        #         print(f"Time {t}: {model.get_variable_attribute(x_vars[(a, t)], poi.VariableAttribute.Value)}")

        return agent_schedules, optimal_objective

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

        total_payment = sum([agent.salary_per_tick for agent in self.model.agents_by_type[ServiceAgent]
                             if self.model.steps in agent.shift_schedule.keys()
                             and agent.shift_schedule[self.model.steps] == True])

        logger.info(
            "Step %d: Revenue: %.2f, Payment: %.2f, Profit: %.2f.",
            self.model.steps,
            total_revenue,
            total_payment,
            total_revenue - total_payment,
        )

        return total_revenue - total_payment

    def update_service_agent_employee_pool(self) -> None:
        """
        Create (new) employee pool of service agents, if one already exists.
        """
        service_agents = []

        # Delete all existing service agents
        if ServiceAgent in self.model.agents_by_type.keys():
            service_agents = list(self.model.agents_by_type[ServiceAgent])

        for agent in service_agents:
            agent.remove()

        # Create value lists for customer_capacity and salary_per_tick
        for _ in range(Config().service.service_agents):
            customer_capacity = np.random.randint(
                Config().service.service_agent_capacity_min,
                Config().service.service_agent_capacity_max,
            )
            salary_per_tick = customer_capacity * (
                    Config().service.service_agent_salary_per_tick
                    / Config().service.service_agent_capacity
            )

            # Create a new service agent with the given values
            service_agent.ServiceAgent.create_agents(
                model=self.model,
                n=1,
                customer_capacity=customer_capacity,
                salary_per_tick=salary_per_tick,
            )

        logger.info(
            "Updated employee pool of service agents. Working agent amount: %d",
            Config().service.service_agents,
        )

    def derive_parameters_from_service_agent_shift_schedule(
            self, service_agent_shift_schedule: dict[ServiceAgent, list[int]]
    ) -> tuple[dict[ServiceAgent, int], dict[ServiceAgent, int], int]:
        """
        Calculate derived parameters resulting from service_agent_shift_schedule for visualization and debugging purposes.
        """
        service_agent_working_hours_count: dict[ServiceAgent, int] = {}
        service_agent_working_shifts_count: dict[ServiceAgent, int] = {}
        working_agents_count: int = 0

        for agent in service_agent_shift_schedule.keys():
            schedule = service_agent_shift_schedule.get(agent, [])
            service_agent_working_hours_count[agent] = sum(schedule)

            shifts = 0
            previous = 0
            for hour in schedule:
                if hour == 1 and previous == 0:
                    shifts += 1
                previous = hour

            service_agent_working_shifts_count[agent] = shifts
            if service_agent_working_hours_count[agent] > 0:
                working_agents_count += 1

        return (
            service_agent_working_hours_count,
            service_agent_working_shifts_count,
            working_agents_count,
        )

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
        # Decision variables
        if self.model.steps == 1:
            if Config().run.use_heuristic_for_first_step_prediction:
                # For the first prediction don't use LSTM model but a simple heuristic based on 80% of the grid size
                predicted_visitors = [int(round(0.8 * Config().restaurant.grid_height * Config().restaurant.grid_width))] * Config().run.full_day_cycle_period
            else:
                # Alternative approach: Create synthetic input with average values
                # Note: Although this approach provides a good approximation for the first 144 steps, it substantially reduces the prediction quality of all further predictions due to the constant synthetic data in the history
                predicted_visitors: list[int] = self.model.lstm_model.forecast(n=Config().run.full_day_cycle_period, first_step=True)
        else:
            predicted_visitors: list[int] = self.model.lstm_model.forecast(n=Config().run.full_day_cycle_period)
        history.add_predicted_customer_agents(predicted_visitors)
        available_service_agents = list(self.model.agents_by_type[ServiceAgent])

        # Optimize the shift schedule
        service_agent_shift_schedule: dict[ServiceAgent, list[int]] = {}
        service_agent_shift_schedule, optimal_obj = self.optimize_shift_schedule(
            available_service_agents, predicted_visitors
        )

        logger.info(
            "Optimized shift schedule computed with optimal objective (total cost): %.2f and shift_schedule: %s",
            optimal_obj,
            [(ag.unique_id, sh) for ag, sh in service_agent_shift_schedule.items()],
        )

        next_step = self.model.steps + 1

        # Update each service agent with their computed schedule
        for agent in available_service_agents:
            # Assume each ServiceAgent has a 'shift_schedule' attribute to store its schedule.
            if agent in service_agent_shift_schedule.keys():
                for i in range(Config().run.full_day_cycle_period):
                    agent.shift_schedule[next_step + i] = service_agent_shift_schedule[agent][i]
            else:
                agent.shift_schedule = [0] * Config().run.full_day_cycle_period

        # Calculate derived parameters resulting from service_agent_shift_schedule
        (
            service_agent_working_hours_count,
            service_agent_working_shifts_count,
            working_agents_count,
        ) = self.derive_parameters_from_service_agent_shift_schedule(service_agent_shift_schedule)
        logger.info(
            "Derived parameters: service_agent_working_hours_count: %s, service_agent_working_shifts_count: %s, working_agents_count: %d",
            service_agent_working_hours_count,
            service_agent_working_shifts_count,
            working_agents_count,
        )

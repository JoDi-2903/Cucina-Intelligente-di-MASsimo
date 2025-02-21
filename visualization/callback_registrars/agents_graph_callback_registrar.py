import json

import plotly.graph_objects as go
from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta
from visualization.messages.dashboard_message import DashboardMessage

# Define lists to store the number of agents over time
_num_agents: list[int] = []
_num_customer_agents: list[int] = []
_num_service_agents: list[int] = []
_num_manager_agents: list[int] = []
_steps: list[int] = []


class AgentsGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        @app.callback(
            Output("agents-graph", "figure"),
            Input('ws', 'message')
        )
        def update_agents_graph(message: str):
            """Update the agents graph that shows the number of agents over time."""
            # Deserialize the JSON message
            print('agent', message)
            if message is None:
                return

            message_dict = json.loads(message)
            dashboard_message = DashboardMessage(**message_dict)

            # Update the steps
            _steps.append(dashboard_message.step)

            # Get the data
            _num_agents.append(dashboard_message.agent_message.num_agents)
            _num_customer_agents.append(dashboard_message.agent_message.num_customer_agents)
            _num_service_agents.append(dashboard_message.agent_message.num_service_agents)
            _num_manager_agents.append(dashboard_message.agent_message.num_manager_agents)

            # Create a new figure
            figure = go.Figure()

            # Add a trace for the number of all agents
            figure.add_trace(go.Scatter(
                x=_steps,
                y=_num_agents,
                mode='lines+markers',
                name="Number of all agents",
                line=dict(color='grey')
            ))

            # Add a trace for the number of customer agents
            figure.add_trace(go.Scatter(
                x=_steps,
                y=_num_customer_agents,
                mode='lines+markers',
                name="Number of customer agents",
                line=dict(color='blue')
            ))

            # Add a trace for the number of service agents
            figure.add_trace(go.Scatter(
                x=_steps,
                y=_num_service_agents,
                mode='lines+markers',
                name="Number of service agents",
                line=dict(color='orange')
            ))

            # Add a trace for the number of manager
            figure.add_trace(go.Scatter(
                x=_steps,
                y=_num_manager_agents, mode='lines+markers',
                name="Number of manager agents",
                line=dict(color='green')
            ))

            # Update the layout
            figure.update_layout(
                title="History of the number of agents",
                xaxis_title="Time steps",
                yaxis_title="Number of agents"
            )

            return figure

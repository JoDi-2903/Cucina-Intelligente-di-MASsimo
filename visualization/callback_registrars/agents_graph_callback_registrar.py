import plotly.graph_objects as go
from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta

# Define lists to store the number of agents over time
_num_agents: list[int] = []
_num_customer_agents: list[int] = []
_num_service_agents: list[int] = []
_num_manager_agents: list[int] = []
_steps: list[int] = []
_i = 0


class AgentsGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        @app.callback(
            Output("agents-graph", "figure"),
            Input('interval-component', 'n_intervals')
        )
        def update_agents_graph(_):
            """Update the agents graph that shows the number of agents over time."""
            global _num_agents, _num_customer_agents, _num_service_agents, _num_manager_agents, _steps, _i

            # Get the data
            from main import restaurant
            _steps.append(_i+1)
            _num_agents.append(len(restaurant.agents))
            # num_customer_agents = len(restaurant.agents_by_type[CustomerAgent])
            # num_service_agents = len(restaurant.agents_by_type[ServiceAgent])
            # num_manager_agents = len(restaurant.agents_by_type[ManagerAgent])

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

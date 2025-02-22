import plotly.graph_objects as go
from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta


class AgentsGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        @app.callback(
            Output("agents-graph", "figure"),
            Input('interval-component', 'n_intervals')
        )
        def update_agents_graph(_):
            """Update the agents graph that shows the number of agents over time."""
            # Lazy import to avoid partial initialization
            from main import history as h

            # Create a new figure
            figure = go.Figure()

            # Add a trace for the number of all agents
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.num_agents_history,
                mode='lines+markers',
                name="Number of all agents",
                line=dict(color='grey')
            ))

            # Add a trace for the number of customer agents
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.num_customer_agents_history,
                mode='lines+markers',
                name="Number of customer agents",
                line=dict(color='blue')
            ))

            # Add a trace for the number of predicted customers agents
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.predicted_customer_growth_history,
                mode='lines+markers',
                name="Predicted customer agents growth",
                line=dict(color='cyan')
            ))

            # Add a trace for the number of service agents
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.num_service_agents_history,
                mode='lines+markers',
                name="Number of service agents",
                line=dict(color='orange')
            ))

            # Add a trace for the number of manager
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.num_manager_agents_history,
                mode='lines+markers',
                name="Number of manager agents",
                line=dict(color='green')
            ))

            # Update the layout
            figure.update_layout(
                title="History of the number of agents",
                xaxis_title="Time steps",
                yaxis_title="Number of agents",
                plot_bgcolor="rgba(30, 30, 30, 1)",
                paper_bgcolor="rgba(20, 20, 20, 1)",
                font=dict(color="white"),
                xaxis=dict(gridcolor="gray"),
                yaxis=dict(gridcolor="gray")
            )

            return figure

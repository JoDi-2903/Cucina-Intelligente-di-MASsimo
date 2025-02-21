import plotly.graph_objects as go
from dash import Dash, Output, Input

from agents.service_agent import logger
from meta_classes.callback_registrar import CallbackRegistrarMeta

_steps: list[int] = []


class TimeSpentGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        @app.callback(
            Output("time-spent-graph", "figure"),
            Input('interval-component', 'n_intervals')
        )
        def update_time_spent_graph(_):
            # Lazy import to avoid partial initialization
            from main import restaurant
            avg_time_spent_history = [
                time / (restaurant.num_customer_agents_history[i] if restaurant.num_customer_agents_history[i] != 0 else 1)
                for i, time in enumerate(restaurant.total_time_spent_history)
            ]
            avg_waiting_time_history = [
                time / restaurant.num_customer_agents_history[i] if restaurant.num_customer_agents_history[i] != 0 else 1
                for i, time in enumerate(restaurant.total_waiting_time_history)
            ]
            logger.info(f"CALLBACK: {restaurant.steps}, {len(restaurant.agents)}")

            # Create a new figure
            figure = go.Figure()

            # Add trace for total time spent
            figure.add_trace(go.Scatter(
                x=restaurant.steps_history,
                y=restaurant.total_time_spent_history,
                mode='lines+markers',
                name="Total time spent",
                line=dict(color='blue')
            ))

            # Add trace for average total time spent
            figure.add_trace(go.Scatter(
                x=restaurant.steps_history,
                y=avg_time_spent_history,
                mode='lines+markers',
                name="Average total time spent",
                line=dict(color='cyan')
            ))

            # Add trace for waiting time
            figure.add_trace(go.Scatter(
                x=restaurant.steps_history,
                y=restaurant.total_waiting_time_history,
                mode='lines+markers',
                name="Waiting time spent",
                line=dict(color='red')
            ))

            # Add trace for average waiting time spent
            figure.add_trace(go.Scatter(
                x=restaurant.steps_history,
                y=avg_waiting_time_history,
                mode='lines+markers',
                name="Average waiting time spent",
                line=dict(color='orange')
            ))

            # Update the layout
            figure.update_layout(
                title="Time spent history",
                xaxis_title="Time steps",
                yaxis_title="Time spent",
                plot_bgcolor="rgba(30, 30, 30, 1)",
                paper_bgcolor="rgba(20, 20, 20, 1)",
                font=dict(color="white"),
                xaxis=dict(gridcolor="gray"),
                yaxis=dict(gridcolor="gray")
            )

            return figure

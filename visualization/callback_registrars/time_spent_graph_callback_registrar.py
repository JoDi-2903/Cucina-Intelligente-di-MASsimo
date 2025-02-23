import logging

import plotly.graph_objects as go
from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta


class TimeSpentGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        # Set the logging level to ERROR to suppress informational messages
        log = logging.getLogger('plotly')
        log.setLevel(logging.ERROR)
        @app.callback(
            Output("time-spent-graph", "figure"),
            Input('interval-component', 'n_intervals')
        )
        def update_time_spent_graph(_):
            # Lazy import to avoid partial initialization
            from main import history as h
            avg_time_spent_history = [
                time / (h.num_customer_agents_history[i] if h.num_customer_agents_history[i] != 0 else 1)
                for i, time in enumerate(h.total_time_spent_history)
            ]
            avg_waiting_time_history = [
                time / (h.num_customer_agents_history[i] if h.num_customer_agents_history[i] != 0 else 1)
                for i, time in enumerate(h.total_waiting_time_history)
            ]

            # Create a new figure
            figure = go.Figure()

            # Add trace for total time spent
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.total_time_spent_history,
                mode='lines+markers',
                name="Total time spent",
                line=dict(color='blue')
            ))

            # Add trace for average total time spent
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=avg_time_spent_history,
                mode='lines+markers',
                name="Average total time spent",
                line=dict(color='cyan')
            ))

            # Add trace for waiting time
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.total_waiting_time_history,
                mode='lines+markers',
                name="Waiting time spent",
                line=dict(color='red')
            ))

            # Add trace for average waiting time spent
            figure.add_trace(go.Scatter(
                x=h.steps_history,
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

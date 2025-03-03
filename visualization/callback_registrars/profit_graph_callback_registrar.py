import plotly.graph_objects as go
import logging
from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta


class ProfitGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        # Set the logging level to ERROR to suppress informational messages
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        @app.callback(
            Output("profit-graph", "figure"),
            Input('interval-component', 'n_intervals')
        )
        def update_profit_graph(_):
            """Update the profit graph that shows the profit growth over time and the profit itself."""
            # Lazy import to avoid partial initialization
            from main import history as h

            # Calculate the cumulative profit
            cumulative_profit = [sum(h.profit_history[:i]) for i in range(1, len(h.profit_history) + 1)]

            # Create a new figure
            figure = go.Figure()

            # Add trace for profit growth
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=cumulative_profit,
                mode='lines+markers',
                name="Cumulative profit",
                line=dict(color='cyan')
            ))

            # Add trace for profit
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.profit_history,
                mode='lines+markers',
                name="Profit",
                line=dict(color='blue')
            ))

            # Update the layout
            figure.update_layout(
                title="Profit history",
                xaxis_title="Time steps",
                yaxis_title="Profit",
                plot_bgcolor="rgba(30, 30, 30, 1)",
                paper_bgcolor="rgba(20, 20, 20, 1)",
                font=dict(color="white"),
                xaxis=dict(gridcolor="gray"),
                yaxis=dict(gridcolor="gray")
            )

            return figure

import json

import plotly.graph_objects as go
from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta
from visualization.messages.dashboard_message import DashboardMessage
from visualization.messages.profit_message import ProfitMessage

_steps: list[int] = []


class ProfitGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        @app.callback(
            Output("profit-graph", "figure"),
            Input('ws', 'message')
        )
        def update_profit_graph(message: str):
            """Update the profit graph that shows the profit growth over time and the profit itself."""
            # Deserialize the JSON message
            print('profit', message)
            if message is None:
                return

            message_dict = json.loads(message)
            dashboard_message = DashboardMessage(**message_dict)

            # Update the steps
            _steps.append(dashboard_message.step)

            # Update the profit graph that shows the profit growth over time and the profit itself
            figure = go.Figure()

            # Add trace for profit growth
            figure.add_trace(go.Scatter(
                x=_steps,
                y=dashboard_message.profit_message.profit_growth,
                mode='lines+markers',
                name="Profit growth",
                line=dict(color='blue')
            ))

            # Add trace for profit
            figure.add_trace(go.Scatter(
                x=_steps,
                y=dashboard_message.profit_message.profit,
                mode='lines+markers',
                name="Profit",
                line=dict(color='orange')
            ))

            # Update the layout
            figure.update_layout(
                title="Profit history",
                xaxis_title="Time steps",
                yaxis_title="Profit / profit growth"
            )

            return figure

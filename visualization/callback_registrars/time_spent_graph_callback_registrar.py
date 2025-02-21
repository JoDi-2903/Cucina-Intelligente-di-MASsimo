import json

import plotly.graph_objects as go
from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta
from visualization.messages.dashboard_message import DashboardMessage

_steps: list[int] = []


class TimeSpentGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        @app.callback(
            Output("time-spent-graph", "figure"),
            Input('ws', 'message')
        )
        def update_time_spent_graph(message: str):
            """Update the waiting time graph that shows the total waiting time."""
            # Deserialize the JSON message
            print('time spent', message)
            if message is None:
                return

            message_dict = json.loads(message)
            dashboard_message = DashboardMessage(**message_dict)

            # Update the steps
            _steps.append(dashboard_message.step)

            # Create the figure
            figure = go.Figure()

            # Add trace for total time spent
            figure.add_trace(go.Scatter(
                x=_steps,
                y=dashboard_message.time_spent_message.total_time_spent,
                mode='lines+markers',
                name="Total time spent",
                line=dict(color='blue')
            ))

            # Add trace for average total time spent
            figure.add_trace(go.Scatter(
                x=_steps,
                y=dashboard_message.time_spent_message.avg_time_spent,
                mode='lines+markers',
                name="Average total time spent",
                line=dict(color='blue')
            ))

            # Add trace for waiting time
            figure.add_trace(go.Scatter(
                x=_steps,
                y=dashboard_message.time_spent_message.total_waiting_time,
                mode='lines+markers',
                name="Waiting time spent",
                line=dict(color='blue')
            ))

            # Add trace for average waiting time spent
            figure.add_trace(go.Scatter(
                x=_steps,
                y=dashboard_message.time_spent_message.avg_waiting_time,
                mode='lines+markers',
                name="Average waiting time spent",
                line=dict(color='blue')
            ))

            # Update the layout
            figure.update_layout(
                title="Time spent history",
                xaxis_title="Time steps",
                yaxis_title="Time spent"
            )

            return figure

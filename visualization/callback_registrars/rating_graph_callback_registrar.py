import plotly.graph_objects as go
from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta


class RatingGraphCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        @app.callback(
            Output("rating-graph", "figure"),
            Input('interval-component', 'n_intervals')
        )
        def update_rating_graph(_):
            """Update the rating graph that shows the profit growth over time and the profit itself."""
            # Lazy import to avoid partial initialization
            from main import history as h

            # Create a new figure
            figure = go.Figure()

            # Add trace for profit
            figure.add_trace(go.Scatter(
                x=h.steps_history,
                y=h.rating_history,
                mode='lines+markers',
                name="Rating",
                line=dict(color='orange')
            ))

            # Update the layout
            figure.update_layout(
                title="Rating history",
                xaxis_title="Time steps",
                yaxis_title="Rating",
                plot_bgcolor="rgba(30, 30, 30, 1)",
                paper_bgcolor="rgba(20, 20, 20, 1)",
                font=dict(color="white"),
                xaxis=dict(gridcolor="gray"),
                yaxis=dict(gridcolor="gray")
            )

            return figure

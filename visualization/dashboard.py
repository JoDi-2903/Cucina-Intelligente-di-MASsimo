import dash_bootstrap_components as dbc
import dash_extensions as de
from dash import Dash, html, dcc
from flask import Flask

from visualization.callback_registrars.agents_graph_callback_registrar import AgentsGraphCallbackRegistrar
from visualization.callback_registrars.profit_graph_callback_registrar import ProfitGraphCallbackRegistrar
from visualization.callback_registrars.time_spent_graph_callback_registrar import TimeSpentGraphCallbackRegistrar


class Dashboard:
    def __init__(self, server: Flask):
        # Initialize dash
        self.app = Dash(
            __name__,
            server=server,
            routes_pathname_prefix='/',
            external_stylesheets=[dbc.themes.DARKLY]
        )

        # Create layout and register callbacks
        self.__create_layout()
        self.__register_callbacks()

    def __create_layout(self):
        self.app.layout = html.Div([
            html.H1("Restaurant metrics dashboard"),

            html.Div([
                dcc.Graph(id="profit-graph"),
                dcc.Graph(id="time-spent-graph")
            ], style={'display': 'flex'}),

            dcc.Graph(id="agents-graph"),

            # WebSocket connections for update events
            de.WebSocket(id='ws', url="ws://127.0.0.1:8080/socket"),
        ], style={'backgroundColor': '#383434'})

    def __register_callbacks(self):
        """Register the callbacks for the dashboard."""
        ProfitGraphCallbackRegistrar().register_callbacks(self.app)
        TimeSpentGraphCallbackRegistrar().register_callbacks(self.app)
        AgentsGraphCallbackRegistrar().register_callbacks(self.app)

    def run(self):
        """Run the dashboard server."""
        self.app.run_server(debug=True, port=8080)

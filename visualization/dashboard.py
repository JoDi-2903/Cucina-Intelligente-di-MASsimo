import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

from visualization.callback_registrars.agents_graph_callback_registrar import AgentsGraphCallbackRegistrar
from visualization.callback_registrars.profit_graph_callback_registrar import ProfitGraphCallbackRegistrar
from visualization.callback_registrars.time_spent_graph_callback_registrar import TimeSpentGraphCallbackRegistrar


class Dashboard:
    def __init__(self):
        # Initialize dash
        self.dash_app = Dash(
            __name__,
            routes_pathname_prefix='/',
            external_stylesheets=[dbc.themes.DARKLY]
        )

        # Create layout and register callbacks
        self.__create_layout()
        self.__register_callbacks()

    def __create_layout(self):
        self.dash_app.layout = html.Div([
            html.H1(
                "Restaurant metrics dashboard",
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'padding': '20px'
                }
            ),

            html.Div(
                [
                    dcc.Graph(id="profit-graph", style={'width': '100%'}),
                    dcc.Graph(id="time-spent-graph", style={'width': '100%'})
                ],
                style={
                    'display': 'flex',
                    'width': '100%',
                    'justify-content': 'space-evenly',
                }
            ),

            dcc.Graph(id="agents-graph"),

            dcc.Interval(
                id='interval-component',
                interval=500,
                n_intervals=0
            )
        ], style={'backgroundColor': 'rgba(20, 20, 20, 1)', 'padding': '12px'})

    def __register_callbacks(self):
        """Register the callbacks for the dash
            dcc.Interval(id='interval-component', interval=5 * 1000, n_intervals=0),board."""
        ProfitGraphCallbackRegistrar().register_callbacks(self.dash_app)
        TimeSpentGraphCallbackRegistrar().register_callbacks(self.dash_app)
        AgentsGraphCallbackRegistrar().register_callbacks(self.dash_app)

    def run(self):
        """Run the dashboard server."""
        self.dash_app.run_server(debug=True)

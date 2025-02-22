import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Dash, html, dcc

from visualization.callback_registrars.agents_graph_callback_registrar import AgentsGraphCallbackRegistrar
from visualization.callback_registrars.auto_refresh_callback_registrar import AutoRefreshCallbackRegistrar
from visualization.callback_registrars.profit_graph_callback_registrar import ProfitGraphCallbackRegistrar
from visualization.callback_registrars.rating_graph_callback_registrar import RatingGraphCallbackRegistrar
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
            html.Div([
                html.H1(
                    "Restaurant metrics dashboard",
                    style={
                        'textAlign': 'center',
                        'color': 'white',
                        'padding': '20px',
                        'flex': '1'
                    }
                ),
                daq.ToggleSwitch(
                    id='auto-refresh-toggle',
                    value=True,
                    label='Auto-refresh',
                    labelPosition='top',
                    style={'marginRight': '10px', 'alignSelf': 'center'},
                    color='#00cc00'  # Default color when on
                ),
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'width': '100%'
            }),

            dcc.Graph(id="profit-graph"),
            dcc.Graph(id="rating-graph"),
            dcc.Graph(id="agents-graph"),
            html.Img(
                id="restaurant-grid-heatmap-image",
                style={
                    'display': 'block',
                    'margin': '0 auto',
                    'padding': '20px'
                }
            ),

            dcc.Graph(id="time-spent-graph"),

            dcc.Interval(
                id='interval-component',
                interval=1000,
                n_intervals=0,
                disabled=False
            )
        ], style={'backgroundColor': 'rgba(20, 20, 20, 1)', 'padding': '12px'})

    def __register_callbacks(self):
        """Register the callbacks for the dash
            dcc.Interval(id='interval-component', interval=5 * 1000, n_intervals=0),board."""
        ProfitGraphCallbackRegistrar().register_callbacks(self.dash_app)
        RatingGraphCallbackRegistrar().register_callbacks(self.dash_app)
        TimeSpentGraphCallbackRegistrar().register_callbacks(self.dash_app)
        AgentsGraphCallbackRegistrar().register_callbacks(self.dash_app)
        AutoRefreshCallbackRegistrar().register_callbacks(self.dash_app)

    def run(self, run_server_in_debug_mode: bool):
        """
        Run the dashboard server.
        :param run_server_in_debug_mode: True if the server should run in debug mode, False otherwise.
        """
        self.dash_app.run_server(debug=run_server_in_debug_mode)

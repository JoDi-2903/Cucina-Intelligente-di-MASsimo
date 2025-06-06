import logging

from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta


class AutoRefreshCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        # Set the logging level to ERROR to suppress informational messages
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        @app.callback(
            [Output('interval-component', 'disabled'),
             Output('auto-refresh-toggle', 'color')],
            Input('auto-refresh-toggle', 'value'),
        )
        def toggle_auto_refresh(value: bool):
            """Toggle the interval component on button click."""
            return not value, ('#00cc00' if value else '#cc0000')

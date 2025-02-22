from dash import Dash, Output, Input

from meta_classes.callback_registrar import CallbackRegistrarMeta


class RestaurantGridHeatmapImageCallbackRegistrar(metaclass=CallbackRegistrarMeta):
    @staticmethod
    def register_callbacks(app: Dash):
        @app.callback(
            Output("restaurant-grid-heatmap-image", "src"),
            Input('interval-component', 'n_intervals')
        )
        def update_time_spent_graph(_):
            """Update the heatmap image of the restaurant grid."""
            # Lazy import to avoid partial initialization
            from main import history as h
            return f'data:image/png;base64,{h.restaurant_grid_heatmap_image}'

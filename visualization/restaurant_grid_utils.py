import base64
import io

import matplotlib
import numpy as np
import seaborn as sns
from matplotlib import colors, pyplot as plt
from matplotlib.figure import Figure

from data_structures.config.config import Config
from models.restaurant_model import RestaurantModel

# Use the Agg backend to avoid the need for a GUI
matplotlib.use("Agg")

# Define the color map for the grid
_CMAP = colors.ListedColormap(["lightgrey", "salmon", "mediumseagreen", "cornflowerblue"])
__BOUNDS = [0, 1, 2, 3, 4]
_NORM = colors.BoundaryNorm(__BOUNDS, _CMAP.N)
_LEGEND_LABELS = [
    'Empty table',
    'Customer agent waits for food',
    'Customer agent is eating',
    'Customer agent finished eating'
]
_DARK_MODE_SCHEME = {
    'figure.facecolor': '#141414',
    'axes.facecolor': '#141414',
    'axes.edgecolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'text.color': 'white'
}


class RestaurantGridUtils:
    """Utility class for the restaurant grid."""

    @staticmethod
    def update_grid_heatmap(restaurant: RestaurantModel):
        """
        Update the heatmap for the restaurant's grid in the global history.
        :param restaurant: The restaurant model to get the grid heatmap for.
        """
        # Create the heatmap with a dark background (dark mode)
        with plt.style.context(_DARK_MODE_SCHEME):
            # Create a new plot with the figure size
            fig, ax = plt.subplots(figsize=(Config().restaurant.grid_width, Config().restaurant.grid_height))
            ax.set_title("The heatmap of the restaurant's grid", fontsize=18, pad=10)

            # Get all cell values for the grid and create the heatmap
            cell_values = RestaurantGridUtils.__get_cell_values(restaurant)
            sns.heatmap(
                cell_values,
                cmap=_CMAP,
                norm=_NORM,
                cbar=True,
                linewidths=0.5,
                linecolor="gray"
            )

            # Add a legend to the plot
            RestaurantGridUtils.__add_legend(ax)

            # Save the plot as a Base64 string in the global history
            from main import history  # Avoid circular import
            history.restaurant_grid_heatmap_image = RestaurantGridUtils.__get_plot_as_base64_image(fig)

    @staticmethod
    def __get_cell_values(restaurant):
        """
        Get the cell values for the restaurant grid.
        :param restaurant: The restaurant model to get the cell values for.
        :return: The cell values for the restaurant grid.
        """
        cell_values = np.zeros((restaurant.grid.width, restaurant.grid.height))
        for agent, (x, y) in restaurant.grid.coord_iter():
            # Set the cell value depending on the agent state
            # 0 = no agent, 1 = waiting for food, 2 = eating, 3 = finished eating
            cell_value: int = 0 if agent is None else agent.state.value

            # Place the cell value on the grid
            cell_values[x][y] = cell_value

        return cell_values

    @staticmethod
    def __add_legend(ax):
        """
        Add a legend to the plot that shows the different agent states.
        :param ax: The axis to add the legend to.
        """
        for i, label in enumerate(_LEGEND_LABELS):
            ax.plot([], [], marker='s', color=_CMAP(i), label=label, linestyle='None')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=1, frameon=False, fontsize=16)

    @staticmethod
    def __get_plot_as_base64_image(fig: Figure) -> str:
        """
        Get the current plot as a Base64 image.
        :return: The Base64 image string of the current plot.
        """
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)  # Move to the beginning of the buffer
        image_bytes = buf.getvalue()
        return base64.b64encode(image_bytes).decode("utf-8")

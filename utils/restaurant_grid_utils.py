import numpy as np
import seaborn as sns
from matplotlib import colors, pyplot as plt

from models.restaurant_model import RestaurantModel

_cmap = colors.ListedColormap(["black", "red", "green", "blue"])
__bounds = [0, 1, 2, 3]
_norm = colors.BoundaryNorm(__bounds, _cmap.N)

class RestaurantGridUtils:
    """Utility class for the restaurant grid."""

    @staticmethod
    def show_grid(restaurant: RestaurantModel):
        """
        Show the passed grid in a seaborn heatmap.
        :param restaurant: The restaurant model to show the grid for.
        """
        # Get all cell values for the grid
        cell_values = np.zeros((restaurant.grid.width, restaurant.grid.height))
        for agent, (x, y) in restaurant.grid.coord_iter():
            # Set the cell value depending on the agent state
            # 0 = no agent, 1 = waiting for food, 2 = eating, 3 = finished eating
            cell_value: int = 0 if agent is None else agent.state.value

            # Place the cell value on the grid
            cell_values[x][y] = cell_value

        sns.heatmap(
            cell_values,
            cmap=_cmap,
            norm=_norm,
            cbar=True,
            linewidths=0.5,
            linecolor="gray"
        )

        plt.show()

import numpy as np
import seaborn as sns
from matplotlib import colors, pyplot as plt

from models.restaurant_model import RestaurantModel


class RestaurantGridUtils:
    """Utility class for the restaurant grid."""

    def __init__(self):
        self.__cmap = colors.ListedColormap(["black", "red", "orange", "green", "blue"])
        self.bounds = [0, 1, 2, 3, 4]
        self.__norm = colors.BoundaryNorm(self.bounds, self.__cmap.N)

        # Create new plot that will be updated dynamically
        plt.ion()
        _, self.__ax = plt.subplots()
        plt.show()

    def show_grid(self, restaurant: RestaurantModel):
        """
        Show the passed grid in a seaborn heatmap.
        :param restaurant: The restaurant model to show the grid for.
        """
        agent_counts = np.zeros((restaurant.grid.width, restaurant.grid.height))
        for agent, (x, y) in restaurant.grid.coord_iter():
            # Set the cell value depending on the agent state
            # 0 = no agent, 1 = waiting for service agent, 2 = waiting for food, 3 = eating, 4 = finished eating
            agent_count = 0 if agent is None else agent.state + 1

            # Place the cell value on the grid
            agent_counts[x][y] = agent_count

        self.__ax.clear()
        sns.heatmap(
            agent_counts,
            cmap=self.__cmap,
            norm=self.__norm,
            cbar=True,
            linewidths=0.5,
            linecolor="gray",
            ax=self.__ax
        )
        plt.pause(0.1)

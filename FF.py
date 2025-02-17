import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap

# For states 0=empty, 1=tree, 2=fire
colors = ['white', 'green', 'red']  
custom_cmap = ListedColormap(colors)


class ForestFireModel:
    def __init__(self, grid_size=50, p_tree=0.01, p_fire=0.0001):
        self.grid_size = grid_size
        self.p_tree = p_tree  # Probability of a tree growing
        self.p_fire = p_fire  # Probability of lightning igniting a tree
        self.grid = np.zeros((grid_size, grid_size), dtype=int)

    def step(self):
        """Simulate one time step of the forest fire model."""
        new_grid = np.copy(self.grid)

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if self.grid[x, y] == 0:  # Empty cell
                    if random.random() < self.p_tree:
                        new_grid[x, y] = 1  # A tree grows
                elif self.grid[x, y] == 1:  # Tree present
                    if random.random() < self.p_fire:
                        new_grid[x, y] = 2  # Tree catches fire
                    else:
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                                if self.grid[nx, ny] == 2:  # Neighboring tree is on fire
                                    new_grid[x, y] = 2
                                    break
                elif self.grid[x, y] == 2:  # Burning tree
                    new_grid[x, y] = 0  # Burnt tree becomes empty

        self.grid = new_grid

    def display(self):
        """Display the grid using matplotlib."""
        cmap = plt.get_cmap("viridis", 3)
        im = ax.imshow(self.grid, cmap=custom_cmap, vmin=0, vmax=2)
        plt.colorbar(ticks=[0, 1, 2], label="Cell State")
        plt.title("Forest Fire Model")
        plt.show()

    def animate(self, steps=100, output_file="forest_fire.mp4"):
        """Create an animation of the forest fire model."""
        fig, ax = plt.subplots()
        cmap = plt.get_cmap("viridis", 3)
        im = ax.imshow(self.grid, cmap=custom_cmap, vmin=0, vmax=2)

        def update(frame):
            self.step()
            im.set_data(self.grid)
            ax.set_title(f"Step {frame}")
            return [im]

        anim = FuncAnimation(fig, update, frames=steps, interval=200, blit=True)
        anim.save(output_file, writer="ffmpeg")
        print(f"Animation saved to {output_file}")

if __name__ == "__main__":
    grid_size = 50
    steps = 100

    model = ForestFireModel(grid_size=50, p_tree=0.05, p_fire=0.0001)
    model.animate(steps=500, output_file="forest_fire.mp4")


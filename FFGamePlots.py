import pygame
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Constants
GRID_SIZE = 50
CELL_SIZE = 10
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
FPS = 10

# Colors
COLORS = {
    0: (255, 255, 255),  # Empty (white)
    1: (0, 255, 0),      # Tree (green)
    2: (255, 0, 0),      # Fire (red)
    "player": (0, 0, 255),  # Player (blue)
    "extinguished": (0, 0, 150)  # Extinguished fire (darker blue)
}

# Forest Fire Model
class ForestFireGame:
    def __init__(self, grid_size, p_tree, p_fire):
        self.grid_size = grid_size
        self.p_tree = p_tree
        self.p_fire = p_fire
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        self.player_pos = [grid_size // 2, grid_size // 2]  # Start in the center
        self.extinguished = 0
        self.burned = 0
        self.extinguish_overlay = np.zeros((grid_size, grid_size), dtype=int)

        # Statistics tracking
        self.time_step = 0
        self.burned_history = []
        self.extinguished_history = []
        self.trees_history = []
        self.fire_percent_history = []
        self.tree_percent_history = []

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
                        for dx, dy in [
                            (-1, -1), (-1, 0), (-1, 1),
                            (0, -1),          (0, 1),
                            (1, -1), (1, 0), (1, 1)
                        ]:  # Moore neighborhood
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                                if self.grid[nx, ny] == 2:  # Neighboring tree is on fire
                                    new_grid[x, y] = 2
                                    break
                elif self.grid[x, y] == 2:  # Burning tree
                    new_grid[x, y] = 0  # Burnt tree becomes empty
                    self.burned += 1
        self.grid = new_grid

        # Decrease the extinguish overlay by 1 each frame (fades out blue cells)
        self.extinguish_overlay[self.extinguish_overlay > 0] -= 1

        # Update statistics
        self.time_step += 1
        self.burned_history.append(self.burned)
        self.extinguished_history.append(self.extinguished)
        self.trees_history.append(np.sum(self.grid == 1))

        total_cells = self.grid_size * self.grid_size
        fire_percent = (np.sum(self.grid == 2) / total_cells) * 100
        tree_percent = (np.sum(self.grid == 1) / total_cells) * 100
        self.fire_percent_history.append(fire_percent)
        self.tree_percent_history.append(tree_percent)

    def move_player(self, direction):
        """Move the player in the specified direction."""
        x, y = self.player_pos
        if "UP" in direction and x > 0:
            x -= 1
        if "DOWN" in direction and x < self.grid_size - 3:
            x += 1
        if "LEFT" in direction and y > 0:
            y -= 1
        if "RIGHT" in direction and y < self.grid_size - 3:
            y += 1
        self.player_pos = [x, y]

        # Extinguish fires in the 3x3 area around the player
        for i in range(x, x + 3):
            for j in range(y, y + 3):
                if 0 <= i < self.grid_size and 0 <= j < self.grid_size:
                    if self.grid[i, j] == 2:
                        self.grid[i, j] = 0
                        self.extinguished += 1
                        self.extinguish_overlay[i, j] = 2  # Add overlay to show extinguished fire

    def get_stats(self):
        """Return the current statistics."""
        return {
            "Burned": self.burned,
            "Extinguished": self.extinguished,
            "Remaining Trees": np.sum(self.grid == 1)
        }

    def draw_dynamic_plot(self):
        """Render the dynamic time-series plot as a surface for pygame."""
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(self.fire_percent_history, label="Fire (% of domain)", color="orange")
        ax.plot(self.tree_percent_history, label="Trees (% of domain)", color="green")
        ax.set_xlabel("Time Steps")
        ax.set_ylabel("Percentages")
        ax.legend()
        ax.set_title("Forest Fire Statistics")

        canvas = FigureCanvas(fig)
        canvas.draw()
        raw_data = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
        raw_data = raw_data.reshape(canvas.get_width_height()[::-1] + (3,))
        raw_data = np.transpose(raw_data, (1, 0, 2))  # Fix the orientation
        plt.close(fig)
        return pygame.surfarray.make_surface(raw_data)

    def draw_cumulative_extinguished_plot(self):
        """Render the cumulative extinguished plot as a surface for pygame."""
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(self.extinguished_history, label="Extinguished (cumulative)", color="blue")
        ax.set_xlabel("Time Steps")
        ax.set_ylabel("Cumulative Count")
        ax.legend()
        ax.set_title("Cumulative Extinguished Fires")

        canvas = FigureCanvas(fig)
        canvas.draw()
        raw_data = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
        raw_data = raw_data.reshape(canvas.get_width_height()[::-1] + (3,))
        raw_data = np.transpose(raw_data, (1, 0, 2))  # Fix the orientation
        plt.close(fig)
        return pygame.surfarray.make_surface(raw_data)

# Game Loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE + 500, WINDOW_SIZE + 150))  # Adjusted space for the plots
    pygame.display.set_caption("Forest Fire Game")
    clock = pygame.time.Clock()

    # Initialize game
    game = ForestFireGame(GRID_SIZE, p_tree=0.05, p_fire=0.0001)

    # Movement state
    directions = set()
    simulation_step_interval = 5  # Number of frames between simulation updates
    simulation_counter = 0

    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear screen

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    directions.add("UP")
                elif event.key == pygame.K_DOWN:
                    directions.add("DOWN")
                elif event.key == pygame.K_LEFT:
                    directions.add("LEFT")
                elif event.key == pygame.K_RIGHT:
                    directions.add("RIGHT")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    directions.discard("UP")
                elif event.key == pygame.K_DOWN:
                    directions.discard("DOWN")
                elif event.key == pygame.K_LEFT:
                    directions.discard("LEFT")
                elif event.key == pygame.K_RIGHT:
                    directions.discard("RIGHT")

        # Move player continuously if any direction keys are held down
        if directions:
            game.move_player(directions)

        # Update simulation only at intervals
        if simulation_counter % simulation_step_interval == 0:
            game.step()

        simulation_counter += 1

        # Draw grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                color = COLORS[game.grid[x, y]]
                if game.extinguish_overlay[x, y] > 0:
                    color = COLORS["extinguished"]  # Show blue overlay for extinguished fires
                rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)

        # Draw player (3x3 area)
        px, py = game.player_pos
        for i in range(px, px + 3):
            for j in range(py, py + 3):
                if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE:
                    player_rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, COLORS["player"], player_rect)

        # Display stats
        stats = game.get_stats()
        pygame.display.set_caption(
            f"Forest Fire Game - Burned: {stats['Burned']} | Extinguished: {stats['Extinguished']} | Trees: {stats['Remaining Trees']}"
        )

        # Draw dynamic plot
        plot_surface = game.draw_dynamic_plot()
        plot_rect = plot_surface.get_rect()
        plot_rect.topleft = (WINDOW_SIZE, 0)
        screen.blit(plot_surface, plot_rect)

        # Draw cumulative extinguished plot
        extinguished_plot_surface = game.draw_cumulative_extinguished_plot()
        extinguished_plot_rect = extinguished_plot_surface.get_rect()
        extinguished_plot_rect.topleft = (WINDOW_SIZE, WINDOW_SIZE // 2)
        screen.blit(extinguished_plot_surface, extinguished_plot_rect)

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()

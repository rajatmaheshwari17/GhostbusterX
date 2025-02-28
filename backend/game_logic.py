"""
game_logic.py

This module contains the backend game logic for the ghostbuster game.
It includes:
  - A 10x10 grid with Cell objects holding inquiry status, color, and probability.
  - A Ghost class that tracks the ghost's location and remaining moves.
  - A Game class that orchestrates inquiries, ghost movements, and probability updates.

The ghost moves up to 3 times. It moves if either:
  - The player inquires the ghost’s exact cell.
  - More than 80% of the cells in the neighborhood (adjacent cells) have been inquired.
  
Cell colors are updated as follows:
  - "red" if the ghost is exactly at that cell.
  - "orange" if the ghost is in a nearby cell.
  - "green" if the ghost is far.

In burst mode (switched separately), the player gets one chance to catch the ghost.
"""

import random

# Global settings
GRID_SIZE = 10
NEARBY_DISTANCE = 1       # Cells adjacent (including diagonals) are considered nearby.
MOVE_NEARBY_THRESHOLD = 0.8  # Ghost moves if >80% of nearby cells are inquired.

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.inquired = False
        self.color = "neutral"
        self.probability = 1 / (GRID_SIZE * GRID_SIZE)  # Uniform initial probability

    def __repr__(self):
        return (f"Cell({self.row},{self.col}, inquired={self.inquired}, "
                f"color={self.color}, prob={self.probability:.2f})")

class Grid:
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.cells = [[Cell(i, j) for j in range(size)] for i in range(size)]

    def get_cell(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.cells[row][col]
        else:
            return None

    def get_nearby_cells(self, row, col, distance=NEARBY_DISTANCE):
        nearby = []
        for i in range(row - distance, row + distance + 1):
            for j in range(col - distance, col + distance + 1):
                if i == row and j == col:
                    continue
                cell = self.get_cell(i, j)
                if cell:
                    nearby.append(cell)
        return nearby

    def all_cells(self):
        for row in self.cells:
            for cell in row:
                yield cell

class Ghost:
    def __init__(self, grid_size=GRID_SIZE):
        self.x = random.randint(0, grid_size - 1)
        self.y = random.randint(0, grid_size - 1)
        self.moves_left = 3

    def position(self):
        return (self.x, self.y)

    def move(self, grid):
        """
        Moves the ghost to a new cell.
        The ghost avoids cells that have been inquired AND have any
        adjacent inquired cells (simulating that it won't move directly
        where the player is nearby). If no valid cell is found, it chooses
        any random cell except its current position.
        """
        possible_positions = []
        for i in range(grid.size):
            for j in range(grid.size):
                if (i, j) == (self.x, self.y):
                    continue
                cell = grid.get_cell(i, j)
                # Avoid cells that are inquired
                if cell.inquired:
                    continue
                # Check the cell’s neighbors; if any neighbor is inquired, skip it.
                nearby = grid.get_nearby_cells(i, j)
                if any(neighbor.inquired for neighbor in nearby):
                    continue
                possible_positions.append((i, j))

        if not possible_positions:
            # Fallback: choose any cell other than current position.
            for i in range(grid.size):
                for j in range(grid.size):
                    if (i, j) != (self.x, self.y):
                        possible_positions.append((i, j))
        new_pos = random.choice(possible_positions)
        self.x, self.y = new_pos
        self.moves_left -= 1
        print(f"Ghost moved to {new_pos}. Moves left: {self.moves_left}")
        return new_pos

class Game:
    def __init__(self):
        self.grid = Grid(GRID_SIZE)
        self.ghost = Ghost(GRID_SIZE)
        self.burst_mode = False
        self.initialize_probabilities()

    def initialize_probabilities(self):
        """
        Sets all cells to have an equal probability.
        """
        total_cells = self.grid.size * self.grid.size
        for cell in self.grid.all_cells():
            cell.probability = 1 / total_cells

    def update_probabilities(self):
        """
        Updates the probability distribution:
          - If the ghost has been exactly found (cell is inquired and is red), that cell gets probability 1.
          - Otherwise, assign uniform probability among all non-inquired cells.
        """
        ghost_x, ghost_y = self.ghost.position()
        ghost_cell = self.grid.get_cell(ghost_x, ghost_y)
        if ghost_cell.inquired and ghost_cell.color == "red":
            for cell in self.grid.all_cells():
                cell.probability = 1.0 if cell == ghost_cell else 0.0
            return

        non_inquired = [cell for cell in self.grid.all_cells() if not cell.inquired]
        count = len(non_inquired)
        if count == 0:
            return
        uniform_prob = 1 / count
        for cell in self.grid.all_cells():
            cell.probability = 0.0 if cell.inquired else uniform_prob

    def is_ghost_nearby(self, row, col):
        """
        Returns True if the ghost is within the defined nearby range.
        """
        ghost_x, ghost_y = self.ghost.position()
        return abs(ghost_x - row) <= NEARBY_DISTANCE and abs(ghost_y - col) <= NEARBY_DISTANCE

    def attempt_ghost_move(self, row, col):
        """
        Checks if the ghost should move based on the current inquiry.
        Conditions for movement:
          - The ghost still has moves left.
          - The player has inquired more than 80% of the cells in the vicinity of the clicked cell,
            OR the player clicked exactly where the ghost is.
        If conditions are met, the ghost moves and probabilities are reinitialized.
        Returns True if the ghost moved.
        """
        if self.ghost.moves_left <= 0:
            return False

        nearby_cells = self.grid.get_nearby_cells(row, col)
        if not nearby_cells:
            return False

        inquired_count = sum(1 for cell in nearby_cells if cell.inquired)
        if (inquired_count / len(nearby_cells) >= MOVE_NEARBY_THRESHOLD) or ((row, col) == self.ghost.position()):
            self.ghost.move(self.grid)
            self.initialize_probabilities()
            return True
        return False

    def inquire_cell(self, row, col):
        """
        Processes the player's inquiry on cell (row, col).
          - Marks the cell as inquired.
          - Updates the cell's color:
              * "red" if the ghost is exactly there.
              * "orange" if the ghost is nearby.
              * "green" if the ghost is far.
          - Checks if ghost should move.
          - Updates probability distribution.
        Returns True if the ghost moved as a result of this inquiry.
        """
        cell = self.grid.get_cell(row, col)
        if cell is None:
            print("Invalid cell coordinates.")
            return False

        if cell.inquired:
            print("Cell already inquired.")
            return False

        cell.inquired = True

        if (row, col) == self.ghost.position():
            cell.color = "red"
            print("Ghost found at this cell!")
        elif self.is_ghost_nearby(row, col):
            cell.color = "orange"
            print("Ghost is nearby!")
        else:
            cell.color = "green"
            print("Ghost is far away.")

        ghost_moved = self.attempt_ghost_move(row, col)
        self.update_probabilities()
        return ghost_moved

    def burst_mode_attempt(self, row, col):
        """
        In burst mode the player gets one chance.
        Returns True if the ghost is caught, else False.
        """
        if (row, col) == self.ghost.position():
            print("Burst mode success! You caught the ghost!")
            return True
        else:
            print("Burst mode failed. You lost your chance.")
            return False

    def switch_to_burst_mode(self):
        """
        Switches the game into burst mode.
        """
        self.burst_mode = True
        print("Switched to burst mode. One chance to catch the ghost!")

    def game_status(self):
        """
        Returns a summary of the current game state.
        If not in burst mode, ghost's location is hidden.
        """
        ghost_pos = self.ghost.position() if self.burst_mode else None
        grid_state = [
            [{"color": cell.color, "probability": round(cell.probability, 2), "inquired": cell.inquired}
             for cell in row]
            for row in self.grid.cells
        ]
        return {
            "ghost_position": ghost_pos,
            "ghost_moves_left": self.ghost.moves_left,
            "burst_mode": self.burst_mode,
            "grid": grid_state
        }

# Example usage and testing when running this module directly.
if __name__ == "__main__":
    game = Game()
    print("Initial game state:")
    print(game.game_status())

    # Simulate some inquiries
    print("\nInquiring cell (0, 0):")
    game.inquire_cell(0, 0)
    print(game.game_status())

    print("\nInquiring cell (1, 1):")
    game.inquire_cell(1, 1)
    print(game.game_status())

    # Switch to burst mode and attempt a burst click.
    game.switch_to_burst_mode()
    ghost_caught = game.burst_mode_attempt(0, 0)
    print("Burst mode attempt result:", ghost_caught)

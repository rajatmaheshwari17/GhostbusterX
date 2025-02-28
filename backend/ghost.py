"""
ghost.py

This module defines the Ghost class for the ghostbuster game.
The ghost starts at a random position on a GRID_SIZE x GRID_SIZE board and
can move up to a fixed number of times (default 3). The ghost avoids cells
that have been inquired as well as cells with neighboring inquiries.
"""

import random

class Ghost:
    def __init__(self, grid_size, moves_allowed=3):
        """
        Initializes a new Ghost instance.

        :param grid_size: The size of the grid (assumed square).
        :param moves_allowed: Maximum number of moves allowed for the ghost.
        """
        self.grid_size = grid_size
        self.moves_left = moves_allowed
        self.x = random.randint(0, grid_size - 1)
        self.y = random.randint(0, grid_size - 1)
        print(f"Initialized ghost at position: ({self.x}, {self.y}) with {self.moves_left} moves.")

    def position(self):
        """
        Returns the current position of the ghost.

        :return: A tuple (x, y) representing the ghost's coordinates.
        """
        return (self.x, self.y)

    def move(self, grid):
        """
        Attempts to move the ghost to a new cell based on the following criteria:
          - The ghost avoids cells that have been inquired.
          - The ghost avoids cells that have any neighboring cells that have been inquired.
          - If no ideal cell is found, it will choose any cell except its current location.

        :param grid: The grid object containing cell information (must implement get_cell and get_nearby_cells).
        :return: The new position (x, y) after the move.
        """
        if self.moves_left <= 0:
            print("No moves left for the ghost.")
            return self.position()

        possible_positions = []
        # Iterate over all cells in the grid.
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) == (self.x, self.y):
                    continue  # Skip current position

                cell = grid.get_cell(i, j)
                if cell.inquired:
                    continue  # Skip cells already inquired

                # Check the cell's neighbors; if any neighbor is inquired, skip this cell.
                nearby_cells = grid.get_nearby_cells(i, j)
                if any(neighbor.inquired for neighbor in nearby_cells):
                    continue

                possible_positions.append((i, j))

        if not possible_positions:
            # Fallback: choose any cell except the current position.
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if (i, j) != (self.x, self.y):
                        possible_positions.append((i, j))
        
        new_pos = random.choice(possible_positions)
        self.x, self.y = new_pos
        self.moves_left -= 1
        print(f"Ghost moved to {new_pos}. Moves left: {self.moves_left}")
        return new_pos

    def can_move(self):
        """
        Checks if the ghost still has moves left.

        :return: True if moves_left is greater than 0, otherwise False.
        """
        return self.moves_left > 0

# Test block for running ghost.py independently
if __name__ == "__main__":
    # Dummy grid implementation for testing purposes.
    class DummyCell:
        def __init__(self):
            self.inquired = False

    class DummyGrid:
        def __init__(self, grid_size):
            self.size = grid_size
            self.cells = [[DummyCell() for _ in range(grid_size)] for _ in range(grid_size)]
        
        def get_cell(self, row, col):
            if 0 <= row < self.size and 0 <= col < self.size:
                return self.cells[row][col]
            return None
        
        def get_nearby_cells(self, row, col, distance=1):
            nearby = []
            for i in range(max(0, row - distance), min(self.size, row + distance + 1)):
                for j in range(max(0, col - distance), min(self.size, col + distance + 1)):
                    if (i, j) == (row, col):
                        continue
                    nearby.append(self.cells[i][j])
            return nearby

    grid_size = 10
    dummy_grid = DummyGrid(grid_size)
    ghost = Ghost(grid_size)
    print("Initial ghost position:", ghost.position())

    # Simulate ghost movement a few times
    for _ in range(3):
        if ghost.can_move():
            ghost.move(dummy_grid)
            print("Ghost new position:", ghost.position())

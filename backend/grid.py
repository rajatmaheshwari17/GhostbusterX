"""
grid.py

This module defines the Grid and Cell classes for the ghostbuster game.
Each Cell represents a position on a 10x10 grid with properties:
  - inquired: whether the cell has been clicked/inquired by the player.
  - color: visual feedback ("neutral", "red", "orange", "green") based on the ghost proximity.
  - probability: initial uniform chance that the ghost is in the cell.
The Grid class creates a 2D grid of Cell objects and offers helper functions
to access cells, fetch neighboring cells, and iterate over all cells.
"""

GRID_SIZE = 10  # Default grid size; can be changed if needed.

class Cell:
    def __init__(self, row, col, grid_size=GRID_SIZE):
        """
        Initialize a cell with a given row and column.
        By default, each cell is not inquired, has a neutral color,
        and starts with a uniform probability.
        """
        self.row = row
        self.col = col
        self.inquired = False
        self.color = "neutral"  # Can be updated to "red", "orange", or "green"
        self.probability = 1 / (grid_size * grid_size)  # Uniform probability initially

    def __repr__(self):
        return (f"Cell({self.row}, {self.col}, inquired={self.inquired}, "
                f"color='{self.color}', prob={self.probability:.2f})")


class Grid:
    def __init__(self, size=GRID_SIZE):
        """
        Initialize the grid with a given size (default is 10x10).
        Creates a 2D list of Cell objects.
        """
        self.size = size
        self.cells = [[Cell(row, col, size) for col in range(size)] for row in range(size)]

    def get_cell(self, row, col):
        """
        Retrieve a cell at the given row and column indices.
        Returns None if the indices are out of bounds.
        """
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.cells[row][col]
        return None

    def get_nearby_cells(self, row, col, distance=1):
        """
        Returns a list of cells within a given radius (distance) from the specified cell.
        The cell itself is excluded.
        
        :param row: Row index of the reference cell.
        :param col: Column index of the reference cell.
        :param distance: The radius within which to search for nearby cells.
        :return: List of neighboring Cell objects.
        """
        nearby = []
        for i in range(max(0, row - distance), min(self.size, row + distance + 1)):
            for j in range(max(0, col - distance), min(self.size, col + distance + 1)):
                if i == row and j == col:
                    continue
                cell = self.get_cell(i, j)
                if cell:
                    nearby.append(cell)
        return nearby

    def all_cells(self):
        """
        Generator to iterate over all cells in the grid.
        """
        for row in self.cells:
            for cell in row:
                yield cell

    def reset_grid(self):
        """
        Resets all cells in the grid to their initial state:
        - Not inquired.
        - Neutral color.
        - Uniform probability.
        """
        total_cells = self.size * self.size
        for cell in self.all_cells():
            cell.inquired = False
            cell.color = "neutral"
            cell.probability = 1 / total_cells

if __name__ == "__main__":
    # Test the Grid and Cell implementation.
    grid = Grid()
    
    print("Initial grid:")
    for row in grid.cells:
        print(row)

    # Test retrieving a specific cell.
    cell_0_0 = grid.get_cell(0, 0)
    print("\nCell at (0, 0):", cell_0_0)

    # Test getting nearby cells for a central cell.
    nearby_cells = grid.get_nearby_cells(5, 5)
    print("\nNearby cells to (5, 5):")
    for cell in nearby_cells:
        print(cell)

    # Example: Update cell (2,2) and display the result.
    cell_2_2 = grid.get_cell(2, 2)
    cell_2_2.inquired = True
    cell_2_2.color = "red"
    print("\nUpdated cell (2, 2):", cell_2_2)

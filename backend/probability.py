"""
probability.py

This module contains functions to update and manage the probability
distribution for the ghostbuster game.

Key functionalities:
  - flood_fill_region: Finds the contiguous region of non-inquired cells
    starting from a given cell.
  - update_probabilities: Updates cell probabilities based on the ghost's
    current position and the cells that have been inquired.
"""

def flood_fill_region(grid, start_row, start_col):
    """
    Performs a flood fill to find all contiguous non-inquired cells starting 
    from (start_row, start_col). This defines the region where the ghost is 
    presumed to be.
    
    :param grid: The grid object providing get_cell and get_nearby_cells methods.
    :param start_row: Row index to start the flood fill.
    :param start_col: Column index to start the flood fill.
    :return: A list of Cell objects in the contiguous non-inquired region.
    """
    start_cell = grid.get_cell(start_row, start_col)
    if start_cell is None or start_cell.inquired:
        return []
    
    region = []
    stack = [(start_row, start_col)]
    visited = set()
    
    while stack:
        r, c = stack.pop()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        cell = grid.get_cell(r, c)
        if cell and not cell.inquired:
            region.append(cell)
            # Consider all neighbors (8-connected)
            for neighbor in grid.get_nearby_cells(r, c, distance=1):
                if not neighbor.inquired and (neighbor.row, neighbor.col) not in visited:
                    stack.append((neighbor.row, neighbor.col))
    return region

def update_probabilities(grid, ghost):
    """
    Updates the probability distribution across the grid.
    
    Behavior:
      - If the ghost is found (its cell is inquired and marked "red"), assign
        that cell a probability of 1.0 and all other cells 0.0.
      - Otherwise, identify the contiguous region of non-inquired cells containing
        the ghost's actual cell. Then assign each cell in that region a uniform
        probability (such that the sum over that region is 1), and assign 0.0 to all
        cells outside that region.
    
    :param grid: The grid object (provides all_cells, get_cell, get_nearby_cells).
    :param ghost: The ghost object (provides position() method).
    """
    ghost_x, ghost_y = ghost.position()
    ghost_cell = grid.get_cell(ghost_x, ghost_y)
    
    # If the ghost has been found, its cell should be red.
    if ghost_cell.inquired and ghost_cell.color == "red":
        for cell in grid.all_cells():
            cell.probability = 1.0 if cell == ghost_cell else 0.0
        return

    # Identify the contiguous non-inquired region containing the ghost.
    region = flood_fill_region(grid, ghost_x, ghost_y)
    if not region:
        # Fallback: assign uniform probability among all non-inquired cells.
        non_inquired = [cell for cell in grid.all_cells() if not cell.inquired]
        if non_inquired:
            prob = 1 / len(non_inquired)
            for cell in grid.all_cells():
                cell.probability = prob if not cell.inquired else 0.0
        return

    # Assign a uniform probability for cells in the ghost's region.
    region_prob = 1 / len(region)
    for cell in grid.all_cells():
        if cell in region:
            cell.probability = region_prob
        else:
            cell.probability = 0.0

# Testing block when running probability.py directly.
if __name__ == "__main__":
    # Define dummy classes to simulate grid and ghost objects.
    class DummyCell:
        def __init__(self, row, col):
            self.row = row
            self.col = col
            self.inquired = False
            self.color = "neutral"
            self.probability = 0.0

        def __repr__(self):
            return f"DummyCell({self.row}, {self.col}, inquired={self.inquired}, prob={self.probability:.2f})"

    class DummyGrid:
        def __init__(self, size):
            self.size = size
            self.cells = [[DummyCell(i, j) for j in range(size)] for i in range(size)]
        
        def get_cell(self, row, col):
            if 0 <= row < self.size and 0 <= col < self.size:
                return self.cells[row][col]
            return None
        
        def get_nearby_cells(self, row, col, distance=1):
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
            for row in self.cells:
                for cell in row:
                    yield cell

    class DummyGhost:
        def __init__(self, x, y):
            self._x = x
            self._y = y
        
        def position(self):
            return (self._x, self._y)

    # Create dummy instances for testing.
    grid_size = 10
    dummy_grid = DummyGrid(grid_size)
    dummy_ghost = DummyGhost(5, 5)

    # Test 1: Initial update; ghost region is the connected non-inquired area.
    update_probabilities(dummy_grid, dummy_ghost)
    print("Initial probabilities (ghost region uniform):")
    for row in dummy_grid.cells:
        print([f"{cell.probability:.2f}" for cell in row])

    # Test 2: Mark some cells as inquired to simulate progress.
    # Inquire some cells around the ghost to restrict its region.
    dummy_grid.get_cell(5, 4).inquired = True
    dummy_grid.get_cell(5, 4).color = "green"
    dummy_grid.get_cell(4, 5).inquired = True
    dummy_grid.get_cell(4, 5).color = "green"

    update_probabilities(dummy_grid, dummy_ghost)
    print("\nProbabilities after inquiring some cells:")
    for row in dummy_grid.cells:
        print([f"{cell.probability:.2f}" for cell in row])

    # Test 3: Simulate ghost found (red cell).
    ghost_cell = dummy_grid.get_cell(5, 5)
    ghost_cell.inquired = True
    ghost_cell.color = "red"
    update_probabilities(dummy_grid, dummy_ghost)
    print("\nProbabilities after ghost is found (should be 1 for ghost cell):")
    for row in dummy_grid.cells:
        print([f"{cell.probability:.2f}" for cell in row])

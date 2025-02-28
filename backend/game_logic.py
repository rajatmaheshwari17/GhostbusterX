"""
game_logic.py

An all-in-one implementation of the Ghostbuster game logic in Python using:
  - A set-based approach to manage probabilities.
  - A 10x10 grid of cells.
  - A Ghost that can move up to 3 times if certain conditions are met.
  - Colors: "red", "orange", "green" for each inquiry.

Usage in a larger project:
  from game_logic import Game

  game = Game()
  game.inquire_cell(3, 3)  # example
  ...
"""

import random

# Grid settings
GRID_SIZE = 10
NEARBY_DISTANCE = 1  # "Nearby" means within 1 cell (including diagonals)
MOVE_NEARBY_THRESHOLD = 0.8  # Ghost moves if >80% of a cell's neighbors are inquired

class Cell:
    """
    Represents a single cell in the 10x10 grid.
    """
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.inquired = False
        self.color = "neutral"   # "red", "orange", "green", or "neutral"
        # Start with uniform probability (0.01 each in a 10x10)
        self.probability = 1.0 / (GRID_SIZE * GRID_SIZE)

    def __repr__(self):
        return (f"Cell(r={self.row}, c={self.col}, inq={self.inquired}, "
                f"color={self.color}, prob={self.probability:.2f})")

class Grid:
    """
    Manages a 2D array of Cell objects.
    """
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.cells = [[Cell(r, c) for c in range(size)] for r in range(size)]

    def get_cell(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.cells[row][col]
        return None

    def get_nearby_cells(self, row, col, distance=NEARBY_DISTANCE):
        """
        Returns all cells within 'distance' in row & col, excluding the cell itself.
        """
        results = []
        for r in range(row - distance, row + distance + 1):
            for c in range(col - distance, col + distance + 1):
                if (r, c) == (row, col):
                    continue
                cell = self.get_cell(r, c)
                if cell:
                    results.append(cell)
        return results

    def all_cells(self):
        for row in self.cells:
            for cell in row:
                yield cell

class Ghost:
    """
    Tracks the ghost's location and movement allowances.
    """
    def __init__(self, grid_size=GRID_SIZE, moves_left=3):
        self.x = random.randint(0, grid_size - 1)
        self.y = random.randint(0, grid_size - 1)
        self.moves_left = moves_left

    def position(self):
        return (self.x, self.y)

    def can_move(self):
        return self.moves_left > 0

    def move(self, grid):
        """
        Attempts to move the ghost to a new location, avoiding inquired cells
        and their neighbors if possible. If no ideal cell is found, it picks
        any random cell other than its current one.
        """
        if self.moves_left <= 0:
            return

        possible_positions = []
        for r in range(grid.size):
            for c in range(grid.size):
                if (r, c) == (self.x, self.y):
                    continue
                cell = grid.get_cell(r, c)
                # Avoid inquired cells
                if cell.inquired:
                    continue
                # Avoid cells whose neighbors are inquired
                neighbors = grid.get_nearby_cells(r, c, distance=1)
                if any(n.inquired for n in neighbors):
                    continue
                possible_positions.append((r, c))

        if not possible_positions:
            # Fallback: any cell except current
            for r in range(grid.size):
                for c in range(grid.size):
                    if (r, c) != (self.x, self.y):
                        possible_positions.append((r, c))

        new_pos = random.choice(possible_positions)
        self.x, self.y = new_pos
        self.moves_left -= 1
        print(f"[Ghost] Moved to {new_pos}, moves left = {self.moves_left}")

class Game:
    """
    Orchestrates the Ghostbuster game:
      - Tracks a grid of cells
      - Tracks the ghost's location and moves
      - Maintains a set of possible positions for the ghost
      - Updates probabilities based on inquiry feedback (red/orange/green)
      - Allows a burst mode attempt
    """
    def __init__(self):
        self.grid = Grid(GRID_SIZE)
        self.ghost = Ghost(GRID_SIZE)
        self.burst_mode = False

        # Initially, all cells are equally possible
        self.possible_positions = {(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)}
        # Make sure probabilities are uniform
        self.update_probabilities()

    def is_ghost_nearby(self, row, col):
        """
        Returns True if the ghost is within NEARBY_DISTANCE of (row, col).
        """
        gx, gy = self.ghost.position()
        return abs(gx - row) <= NEARBY_DISTANCE and abs(gy - col) <= NEARBY_DISTANCE

    def inquire_cell(self, row, col):
        """
        The player inquires (clicks) a cell:
          - If the ghost is there => color = red
          - If the ghost is near => color = orange
          - Else => color = green
        Then apply constraints, recalc probabilities, and possibly move the ghost.
        Returns True if the ghost moved, otherwise False.
        """
        cell = self.grid.get_cell(row, col)
        if not cell or cell.inquired:
            return False

        cell.inquired = True
        ghost_x, ghost_y = self.ghost.position()

        # Determine color
        if (row, col) == (ghost_x, ghost_y):
            cell.color = "red"
            print("[Game] Ghost found here!")
        elif self.is_ghost_nearby(row, col):
            cell.color = "orange"
            print("[Game] Ghost is nearby!")
        else:
            cell.color = "green"
            print("[Game] Ghost is far.")

        # Apply constraints to possible positions
        self.apply_constraints(row, col, cell.color)
        # Recalculate probabilities
        self.update_probabilities()

        # Attempt ghost move if conditions are met
        ghost_moved = self.attempt_ghost_move(row, col)
        return ghost_moved

    def apply_constraints(self, row, col, color):
        """
        Updates the set of possible positions based on the color feedback:
          - red: ghost must be exactly here
          - orange: ghost must be in the neighbors
          - green: ghost cannot be in or near this cell
        """
        if color == "red":
            # Only this cell remains possible
            self.possible_positions = {(row, col)}
            return

        # Gather neighbors
        neighbors = self.grid.get_nearby_cells(row, col, distance=1)
        neighbor_coords = {(n.row, n.col) for n in neighbors}
        clicked_coord = (row, col)

        if color == "orange":
            # Keep only the neighbors
            self.possible_positions = self.possible_positions.intersection(neighbor_coords)
        elif color == "green":
            # Remove this cell and its neighbors
            to_remove = neighbor_coords.union({clicked_coord})
            self.possible_positions = self.possible_positions.difference(to_remove)

    def update_probabilities(self):
        """
        Redistribute probabilities among the cells in self.possible_positions.
        If there's exactly one cell left (red scenario), that cell = 1.0.
        Otherwise, uniform distribution among all possible cells.
        """
        # First, set all to 0
        for c in self.grid.all_cells():
            c.probability = 0.0

        count = len(self.possible_positions)
        if count == 0:
            # Edge case: No possible positions left (shouldn't happen if logic is consistent)
            print("[Warning] No possible positions remain!")
            return

        prob_each = 1.0 / count
        for (r, c) in self.possible_positions:
            cell = self.grid.get_cell(r, c)
            cell.probability = prob_each

    def attempt_ghost_move(self, row, col):
        """
        Checks if the ghost should move. We reuse the rule:
          - If the inquired cell is exactly the ghost location (red) OR
          - If >80% of the cell's neighbors have been inquired
        and the ghost still has moves left, it moves.

        After moving, we reset possible_positions to all 100 cells
        (or you can refine this if you want to keep old constraints).
        """
        if not self.ghost.can_move():
            return False

        cell = self.grid.get_cell(row, col)
        neighbors = self.grid.get_nearby_cells(row, col, distance=1)
        inquired_count = sum(n.inquired for n in neighbors)
        threshold = int(MOVE_NEARBY_THRESHOLD * len(neighbors))

        # Condition 1: exact location inquired => red
        # (We allow the ghost to move if it still has moves left)
        if cell.color == "red":
            pass

        # Condition 2: >80% neighbors inquired
        if cell.color == "red" or (inquired_count >= threshold and len(neighbors) > 0):
            old_pos = self.ghost.position()
            self.ghost.move(self.grid)
            new_pos = self.ghost.position()
            if new_pos != old_pos:
                # Reset possible positions or refine them (your choice).
                # Here, we reset to all cells to keep it simple.
                self.possible_positions = {(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)}
                self.update_probabilities()
                return True

        return False

    def burst_mode_attempt(self, row, col):
        """
        In burst mode, the player gets exactly one attempt to catch the ghost.
        Return True if successful, else False.
        """
        if (row, col) == self.ghost.position():
            print("[Game] Burst mode success! Ghost caught!")
            return True
        print("[Game] Burst mode failed!")
        return False

    def switch_to_burst_mode(self):
        """
        Switches the game into burst mode. The next cell click is the final guess.
        """
        self.burst_mode = True
        print("[Game] Burst mode activated! One chance to click the ghost's location.")

    def game_status(self):
        """
        Returns a dictionary summarizing the current state for the UI.
        If not in burst mode, we typically don't reveal the ghost position in a real game.
        """
        ghost_pos = self.ghost.position() if self.burst_mode else None
        grid_info = []
        for r in range(GRID_SIZE):
            row_data = []
            for c in range(GRID_SIZE):
                cell = self.grid.get_cell(r, c)
                # Round to 2 decimals so UI can display f"{prob:.2f}"
                row_data.append({
                    "inquired": cell.inquired,
                    "color": cell.color,
                    "probability": round(cell.probability, 2)
                })
            grid_info.append(row_data)

        return {
            "ghost_position": ghost_pos,
            "ghost_moves_left": self.ghost.moves_left,
            "burst_mode": self.burst_mode,
            "grid": grid_info
        }

# Quick test block if you run game_logic.py directly
if __name__ == "__main__":
    game = Game()
    print("[Test] Initial probabilities:")
    for r in range(GRID_SIZE):
        row_str = []
        for c in range(GRID_SIZE):
            cell = game.grid.get_cell(r, c)
            row_str.append(f"{cell.probability:.2f}")
        print(" ".join(row_str))

    print("\n[Test] Inquiring cell (5,5)...")
    game.inquire_cell(5, 5)
    # Print updated probabilities
    for r in range(GRID_SIZE):
        row_str = []
        for c in range(GRID_SIZE):
            cell = game.grid.get_cell(r, c)
            row_str.append(f"{cell.probability:.2f}")
        print(" ".join(row_str))

    # Example of switching to burst mode
    game.switch_to_burst_mode()
    success = game.burst_mode_attempt(5, 5)
    print(f"[Test] Burst mode result: {success}")

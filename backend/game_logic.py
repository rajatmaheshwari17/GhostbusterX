"""
game_logic.py

Uses a distance-based color assignment:
  - distance=0 => "red"
  - distance=1 => "orange"
  - distance=2 => "yellow"
  - distance>2 => "green"

Then calls a fuzzy-likelihood Bayesian update in bayes_updates.py
so the entire grid is updated each time, not just the local 3x3 region.
"""

import random
from backend.bayes_updates import apply_bayes_update  # We'll define a 4-color approach there

GRID_SIZE = 8
MOVE_NEARBY_THRESHOLD = 0.75  # ghost moves if >= 75% neighbors inquired

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.inquired = False
        self.color = "neutral"
        # Start uniform
        self.probability = 1.0 / (GRID_SIZE * GRID_SIZE)

    def __repr__(self):
        return (f"Cell(r={self.row}, c={self.col}, inq={self.inquired}, "
                f"color={self.color}, prob={self.probability:.2f})")

class Grid:
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.cells = [[Cell(r, c) for c in range(size)] for r in range(size)]

    def get_cell(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.cells[row][col]
        return None

    def all_cells(self):
        for row in self.cells:
            for cell in row:
                yield cell

    def get_nearby_cells(self, row, col, distance=1):
        """Returns up to a 3x3 block around (row,col)."""
        results = []
        for r in range(row - distance, row + distance + 1):
            for c in range(col - distance, col + distance + 1):
                if (r, c) == (row, col):
                    continue
                cell = self.get_cell(r, c)
                if cell:
                    results.append(cell)
        return results

class Ghost:
    def __init__(self, grid_size=GRID_SIZE, moves_left=0):
        self.x = random.randint(0, grid_size - 1)
        self.y = random.randint(0, grid_size - 1)
        self.moves_left = moves_left

    def position(self):
        return (self.x, self.y)

    def can_move(self):
        return self.moves_left > 0

    def move(self, grid):
        if self.moves_left <= 0:
            return
        possible_positions = []
        for r in range(grid.size):
            for c in range(grid.size):
                if (r, c) == (self.x, self.y):
                    continue
                cell = grid.get_cell(r, c)
                if cell.inquired:
                    continue
                possible_positions.append((r, c))
        if not possible_positions:
            print("[Ghost] No valid positions to move to. Staying put.")
            return
        new_pos = random.choice(possible_positions)
        self.x, self.y = new_pos
        self.moves_left -= 1
        print(f"[Ghost] Moved to {new_pos}, moves left = {self.moves_left}")

class Game:
    def __init__(self):
        self.grid = Grid(GRID_SIZE)
        self.ghost = Ghost(GRID_SIZE, moves_left=0)  # set moves_left>0 if you want ghost to move
        self.burst_mode = False
        # Optional: a set of possible positions. We won't forcibly zero out cells though.
        self.possible_positions = {(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)}

    def inquire_cell(self, row, col):
        cell = self.grid.get_cell(row, col)
        if not cell or cell.inquired:
            return False

        # Mark cell as inquired
        cell.inquired = True

        # Compute distance to ghost
        gx, gy = self.ghost.position()
        dist = max(abs(gx - row), abs(gy - col))  # Chebyshev distance

        # Assign color based on distance
        if dist == 0:
            color = "red"
        elif dist == 1:
            color = "orange"
        elif dist == 2:
            color = "yellow"
        else:
            color = "green"
        cell.color = color

        # Optionally apply constraints (we won't forcibly zero out cells)
        self.apply_constraints(row, col, color)

        # Perform Bayesian update (which recognizes "red", "orange", "yellow", "green")
        apply_bayes_update(self.grid, row, col, color)

        # Attempt ghost move if threshold is met
        ghost_moved = self.attempt_ghost_move(row, col)
        return ghost_moved

    def apply_constraints(self, row, col, color):
        # If you want to keep or remove constraints is your call.
        # We'll just keep the same logic, but won't force zero probabilities.
        if color == "red":
            self.possible_positions = {(row, col)}
            return
        neighbors = self.grid.get_nearby_cells(row, col, distance=1)
        neighbor_coords = {(n.row, n.col) for n in neighbors}
        clicked_coord = (row, col)
        if color == "orange":
            self.possible_positions = self.possible_positions.intersection(neighbor_coords)
        elif color in ("green", "yellow"):
            # If you want "yellow" to behave more like orange, change logic here
            to_remove = neighbor_coords.union({clicked_coord})
            self.possible_positions = self.possible_positions.difference(to_remove)

    def attempt_ghost_move(self, row, col):
        if not self.ghost.can_move():
            return False
        cell = self.grid.get_cell(row, col)
        neighbors = self.grid.get_nearby_cells(row, col, distance=1)
        inquired_count = sum(n.inquired for n in neighbors)
        threshold = int(MOVE_NEARBY_THRESHOLD * len(neighbors))
        if cell.color == "red" or (inquired_count >= threshold and len(neighbors) > 0):
            old_pos = self.ghost.position()
            self.ghost.move(self.grid)
            new_pos = self.ghost.position()
            if new_pos != old_pos:
                if cell.color == "red":
                    self.possible_positions.discard((row, col))
                self.possible_positions = {(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)}
                return True
        return False

    def burst_mode_attempt(self, row, col):
        if (row, col) == self.ghost.position():
            print("[Game] Burst mode success! Ghost caught!")
            return True
        print("[Game] Burst mode failed!")
        return False

    def switch_to_burst_mode(self):
        self.burst_mode = True
        print("[Game] Burst mode activated!")

    def game_status(self):
        ghost_pos = self.ghost.position() if self.burst_mode else None
        grid_info = []
        for r in range(GRID_SIZE):
            row_data = []
            for c in range(GRID_SIZE):
                cell = self.grid.get_cell(r, c)
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
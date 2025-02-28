"""
game_logic.py

Demonstration of a region-based probability update with a 5×5 region:
  1. Initially, all cells have equal probability (1 / (GRID_SIZE * GRID_SIZE)).
  2. After each inquiry, the region around the ghost (ghost cell + the 24 surrounding cells)
     is multiplied by a "boost" factor, and cells outside that region are multiplied by
     a "decrease" factor.
  3. Once the player inquires the correct region, probabilities for that region become
     significantly higher, and others become lower.

This is a heuristic approach to "guide" the player, not a strict Bayesian update.
"""

import random

GRID_SIZE = 10
NEARBY_DISTANCE = 1
MOVE_NEARBY_THRESHOLD = 0.8

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.inquired = False
        self.color = "neutral"
        # Start with uniform probability
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

class Ghost:
    def __init__(self, grid_size=GRID_SIZE, moves_left=3):
        self.x = random.randint(0, grid_size - 1)
        self.y = random.randint(0, grid_size - 1)
        # If you don't want the ghost to move at all, set moves_left=0
        self.moves_left = 0  # or 'moves_left' if you want to allow movement

    def position(self):
        return (self.x, self.y)

    def can_move(self):
        return self.moves_left > 0

    def move(self, grid):
        """
        Attempt to move the ghost to a new location, avoiding inquired cells.
        If no valid position is found, the ghost stays put.
        """
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
        self.ghost = Ghost(GRID_SIZE)
        self.burst_mode = False
        # Initially, all cells are equally possible
        self.possible_positions = {(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)}

    def is_ghost_nearby(self, row, col):
        gx, gy = self.ghost.position()
        return abs(gx - row) <= NEARBY_DISTANCE and abs(gy - col) <= NEARBY_DISTANCE

    def inquire_cell(self, row, col):
        cell = self.grid.get_cell(row, col)
        if not cell or cell.inquired:
            return False

        cell.inquired = True
        gx, gy = self.ghost.position()

        if (row, col) == (gx, gy):
            cell.color = "red"
            print("[Game] Ghost found here!")
        elif self.is_ghost_nearby(row, col):
            cell.color = "orange"
            print("[Game] Ghost is nearby!")
        else:
            cell.color = "green"
            print("[Game] Ghost is far.")

        # Apply constraints based on color
        self.apply_constraints(row, col, cell.color)
        # Then apply region-based probability updates
        self.apply_region_based_probabilities(cell.color)
        # Attempt ghost move (if moves_left > 0)
        ghost_moved = self.attempt_ghost_move(row, col)

        return ghost_moved

    def apply_constraints(self, row, col, color):
        """
        If you still want to remove impossible cells, do it here:
          - red: only that cell remains possible
          - orange: only neighbors remain possible
          - green: remove that cell + neighbors
        """
        if color == "red":
            self.possible_positions = {(row, col)}
            return

        neighbors = self.grid.get_nearby_cells(row, col, distance=1)
        neighbor_coords = {(n.row, n.col) for n in neighbors}
        clicked_coord = (row, col)

        if color == "orange":
            self.possible_positions = self.possible_positions.intersection(neighbor_coords)
        elif color == "green":
            to_remove = neighbor_coords.union({clicked_coord})
            self.possible_positions = self.possible_positions.difference(to_remove)

    def apply_region_based_probabilities(self, color):
        """
        A "heuristic" approach:
          1. If color is "red", that means the ghost is exactly here => set that cell to 1, all else 0.
          2. Otherwise, find the ghost's 5x5 region. Multiply region probabilities by a "boost" factor,
             and multiply everything else by a "decrease" factor, then normalize.
        """
        # If the ghost was found exactly, set that cell to 1.0
        if color == "red" and len(self.possible_positions) == 1:
            r, c = list(self.possible_positions)[0]
            # Force that cell to 1, everything else 0
            for cell in self.grid.all_cells():
                cell.probability = 0.0
            self.grid.get_cell(r, c).probability = 1.0
            return

        # Identify the "ghost region" as a 5×5 block around the ghost
        gx, gy = self.ghost.position()
        ghost_region = []
        # Expand from (gx - 2) to (gx + 2) => 5×5 region total
        for rr in range(gx - 2, gx + 3):
            for cc in range(gy - 2, gy + 3):
                cell = self.grid.get_cell(rr, cc)
                if cell:
                    ghost_region.append(cell)

        # Choose multipliers
        region_boost = 1.5
        outside_decrease = 0.8

        # Multiply probabilities
        for cell in self.grid.all_cells():
            # Only update cells still in possible_positions
            if (cell.row, cell.col) not in self.possible_positions:
                cell.probability = 0.0
                continue

            if cell in ghost_region:
                cell.probability *= region_boost
            else:
                cell.probability *= outside_decrease

        # Normalize so sum == 1
        total = sum(cell.probability for cell in self.grid.all_cells())
        if total < 1e-12:
            # Edge case if everything is zero
            print("[Warning] All probabilities ended up zero. Resetting to uniform in possible_positions.")
            count = len(self.possible_positions)
            if count == 0:
                return
            for (r, c) in self.possible_positions:
                self.grid.get_cell(r, c).probability = 1.0 / count
            return

        for cell in self.grid.all_cells():
            if cell.probability > 0:
                cell.probability /= total

    def attempt_ghost_move(self, row, col):
        """
        If conditions are met, the ghost moves, then we reset possible_positions
        or re-apply constraints. We'll keep it simple:
          - If the cell is red or >80% neighbors inquired, ghost moves.
        """
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
                # After moving, reset possible positions to all, or refine further
                self.possible_positions = {(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)}
                # Then do another region-based update if you like
                self.apply_region_based_probabilities("orange")  # or "green", or just none
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
        """
        Returns data for the UI: color, probability, etc.
        """
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

if __name__ == "__main__":
    game = Game()
    print("[Test] Initial probabilities (should be uniform 0.01):")
    for r in range(GRID_SIZE):
        row_str = []
        for c in range(GRID_SIZE):
            cell = game.grid.get_cell(r, c)
            row_str.append(f"{cell.probability:.2f}")
        print(" ".join(row_str))

    print("\n[Test] Inquiring cell (5,5)...")
    game.inquire_cell(5, 5)

    print("[Test] Updated probabilities after 5×5 region-based logic:")
    for r in range(GRID_SIZE):
        row_str = []
        for c in range(GRID_SIZE):
            cell = game.grid.get_cell(r, c)
            row_str.append(f"{cell.probability:.2f}")
        print(" ".join(row_str))

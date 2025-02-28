"""
game_logic.py

Region-based probability update that also handles ghost movement,
WITHOUT reverting the old "red" cell to "neutral." The old red cell
keeps its color but ends up with probability 0 if the ghost moves away.
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
    def __init__(self, grid_size=GRID_SIZE, moves_left=25):
        self.x = random.randint(0, grid_size - 1)
        self.y = random.randint(0, grid_size - 1)
        self.moves_left = moves_left

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
                # Avoid inquired cells
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

        # If probability is 0.0, we still check if it's near the ghost
        if cell.probability == 0.0:
            gx, gy = self.ghost.position()
            if abs(gx - row) <= 1 and abs(gy - col) <= 1:
                # It's near the ghost, so color it orange
                cell.color = "orange"
                print("[Game] 0.0-prob cell is near the ghost! Marking orange but ignoring constraints.")
            else:
                # Otherwise color it green
                cell.color = "green"
                print("[Game] 0.0-prob cell is far from the ghost. Marking green, ignoring constraints.")

            cell.inquired = True
            # Return without constraints or probability updates
            return False

        # Otherwise, normal inquiry logic:
        cell.inquired = True
        gx, gy = self.ghost.position()

        if (row, col) == (gx, gy):
            cell.color = "red"
        elif self.is_ghost_nearby(row, col):
            cell.color = "orange"
        else:
            cell.color = "green"

        self.apply_constraints(row, col, cell.color)
        self.apply_region_based_probabilities()
        ghost_moved = self.attempt_ghost_move(row, col)
        return ghost_moved


    def apply_constraints(self, row, col, color):
        """
        Remove impossible positions from self.possible_positions, if desired.
        - red: only that cell remains possible
        - orange: only neighbors remain possible
        - green: remove that cell + neighbors
        """
        if color == "red":
            # We won't revert color if the ghost moves away,
            # but this cell is "where it was found" at inquiry time.
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

    def apply_region_based_probabilities(self):
        """
        A simple "heuristic" approach:
          - We do NOT force a 'red' cell to 1.0 because the ghost may move away.
          - Instead, we find the ghost's 3x3 region, multiply region probabilities by 1.5,
            multiply others by 0.8, then normalize so sum=1.
        """
        gx, gy = self.ghost.position()
        ghost_region = []
        for rr in range(gx - 1, gx + 2):
            for cc in range(gy - 1, gy + 2):
                cell = self.grid.get_cell(rr, cc)
                if cell:
                    ghost_region.append(cell)

        region_boost = 1.5
        outside_decrease = 0.8

        for cell in self.grid.all_cells():
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
        If conditions are met, the ghost moves. Then we reset possible_positions
        and re-apply region-based logic for the ghost's new location.

        We do NOT revert a 'red' cell to 'neutral' if the ghost moves.
        Instead, we remove that old red cell from possible_positions (prob = 0),
        so the distribution centers around the new position.
        """
        if not self.ghost.can_move():
            return False

        cell = self.grid.get_cell(row, col)
        neighbors = self.grid.get_nearby_cells(row, col, distance=1)
        inquired_count = sum(n.inquired for n in neighbors)
        threshold = int(MOVE_NEARBY_THRESHOLD * len(neighbors))

        # Condition: "red" or >80% neighbors inquired
        if cell.color == "red" or (inquired_count >= threshold and len(neighbors) > 0):
            old_pos = self.ghost.position()
            self.ghost.move(self.grid)
            new_pos = self.ghost.position()
            if new_pos != old_pos:
                # The ghost has moved away from the old location
                if cell.color == "red":
                    # Keep the cell visually red, but remove it from possible_positions
                    self.possible_positions.discard((row, col))

                # Reset possible positions to all cells
                self.possible_positions = {(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)}
                # Also remove the old red cell if you want it to remain at probability 0
                # (since the ghost is definitely not there now).
                # The line above re-includes it, so let's discard it again:
                if cell.color == "red":
                    self.possible_positions.discard((row, col))

                # Re-apply region-based logic for the ghost's new location
                self.apply_region_based_probabilities()
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

# Test block
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
    ghost_moved = game.inquire_cell(5, 5)

    print(f"[Test] Ghost moved? {ghost_moved}")
    print("[Test] Updated probabilities after region-based logic (and possibly ghost movement):")
    for r in range(GRID_SIZE):
        row_str = []
        for c in range(GRID_SIZE):
            cell = game.grid.get_cell(r, c)
            row_str.append(f"{cell.probability:.2f}")
        print(" ".join(row_str))

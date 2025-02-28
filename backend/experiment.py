'''
    def get_ghost_block(self):
        """
        Returns a list of up to 9 cells in the 3x3 region centered on the ghost.
        Includes the ghost cell plus the 8 neighbors (if within bounds).
        """
        gx, gy = self.ghost.position()
        ghost_block = []
        for rr in range(gx - 1, gx + 2):  # gx-1, gx, gx+1
            for cc in range(gy - 1, gy + 2):  # gy-1, gy, gy+1
                cell = self.grid.get_cell(rr, cc)
                if cell:
                    ghost_block.append(cell)
        return ghost_block

    def attempt_ghost_move(self):
        if not self.ghost.can_move():
            return False

        # Gather the 3x3 region around the ghost
        ghost_block = self.get_ghost_block()
        block_size = len(ghost_block)  # Could be up to 9

        # Count how many are orange
        orange_count = sum(cell.color == "orange" for cell in ghost_block)

        # 75% threshold: use math.ceil to avoid flooring
        threshold = math.ceil(0.50 * block_size)

        print(f"[DEBUG] ghost_block_size={block_size}, orange_count={orange_count}, threshold={threshold}")

        if orange_count >= threshold:
            old_pos = self.ghost.position()
            self.ghost.move(self.grid)  # The ghost’s move logic
            new_pos = self.ghost.position()
            if new_pos != old_pos:
                print("[DEBUG] Ghost moved because 50% of its block is orange!")
                # Possibly reset possible_positions or do other logic here
                return True

        return False
    '''
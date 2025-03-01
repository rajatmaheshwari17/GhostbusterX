"""
ui_components.py

This module defines reusable UI components for the Ghostbuster game.
Components include:
  - CellButton: A custom button representing a grid cell.
  - ControlPanel: A frame containing control buttons (Burst Mode and Restart).
  - StatusLabel: A label for displaying game status messages.
  - GridFrame: A container that creates and manages a grid of CellButtons.
"""

import tkinter as tk

class CellButton(tk.Button):
    def __init__(self, master, row, col, command, **kwargs):
        """
        Initializes a CellButton.

        :param master: Parent widget.
        :param row: Row coordinate of the cell.
        :param col: Column coordinate of the cell.
        :param command: Function to call when the cell is clicked (receives row and col).
        """
        self.row = row
        self.col = col
        super().__init__(
            master,
            command=lambda: command(row, col),
            width=8,
            height=5,
            **kwargs
        )

    def update_state(self, inquired, color, probability):
        """
        Updates the button appearance based on the cell state.
        
        :param inquired: Boolean indicating if the cell was inquired.
        :param color: String representing the cell color state ("red", "orange", "green", or "neutral").
        :param probability: Float value for the cell probability.
        """
        # Set text to display probability if cell was inquired; otherwise, empty.
        self.config(text=f"{probability:.2f}" if inquired else "")
        
        # Map the logical color to an actual background color.
        if color == "red":
            bg_color = "red"
        elif color == "orange":
            bg_color = "orange"
        elif color == "green":
            bg_color = "green"
        else:
            bg_color = "SystemButtonFace"  # default system color
        
        self.config(bg=bg_color)

class ControlPanel(tk.Frame):
    def __init__(self, master, burst_command, restart_command, **kwargs):
        """
        A control panel with buttons for Burst Mode and Restart actions.
        
        :param master: Parent widget.
        :param burst_command: Function to call when Burst Mode is activated.
        :param restart_command: Function to call to restart the game.
        """
        super().__init__(master, **kwargs)
        self.burst_button = tk.Button(self, text="Burst Mode", command=burst_command)
        self.burst_button.grid(row=0, column=0, padx=5)
        
        self.restart_button = tk.Button(self, text="Restart Game", command=restart_command)
        self.restart_button.grid(row=0, column=1, padx=5)

class StatusLabel(tk.Label):
    def __init__(self, master, **kwargs):
        """
        A label to display game status messages.
        
        :param master: Parent widget.
        """
        super().__init__(master, **kwargs)
    
    def update_status(self, text):
        """
        Updates the displayed status text.
        
        :param text: New status message.
        """
        self.config(text=text)

class GridFrame(tk.Frame):
    def __init__(self, master, rows, cols, cell_command, **kwargs):
        """
        A container that creates and manages a grid of CellButtons.
        
        :param master: Parent widget.
        :param rows: Number of rows in the grid.
        :param cols: Number of columns in the grid.
        :param cell_command: Function to call when any cell is clicked.
        """
        super().__init__(master, **kwargs)
        self.rows = rows
        self.cols = cols
        self.cell_command = cell_command
        self.cells = [[None for _ in range(cols)] for _ in range(rows)]
        self.create_grid()
    
    def create_grid(self):
        """Creates the grid of CellButtons."""
        for i in range(self.rows):
            for j in range(self.cols):
                cell_btn = CellButton(self, i, j, command=self.cell_command)
                cell_btn.grid(row=i, column=j, padx=1, pady=1)
                self.cells[i][j] = cell_btn

    def update_grid(self, grid_state):
        """
        Updates the grid of buttons based on the provided state.
        
        :param grid_state: A 2D list of dictionaries containing keys:
                           "inquired", "color", and "probability".
        """
        for i in range(self.rows):
            for j in range(self.cols):
                cell_info = grid_state[i][j]
                self.cells[i][j].update_state(
                    inquired=cell_info["inquired"],
                    color=cell_info["color"],
                    probability=cell_info["probability"]
                )

    def disable_all(self):
        """Disables all cell buttons."""
        for row in self.cells:
            for cell in row:
                cell.config(state=tk.DISABLED)

    def enable_all(self):
        """Enables all cell buttons."""
        for row in self.cells:
            for cell in row:
                cell.config(state=tk.NORMAL)

# Quick test of the UI components when running this module directly.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("UI Components Test")

    # Dummy cell command function.
    def dummy_cell_command(row, col):
        print(f"Cell clicked at ({row}, {col})")
    
    # Dummy burst and restart commands.
    def dummy_burst_command():
        print("Burst Mode activated")
    
    def dummy_restart_command():
        print("Game restarted")

    # Create and pack the grid.
    grid_frame = GridFrame(root, rows=10, cols=10, cell_command=dummy_cell_command)
    grid_frame.pack(padx=10, pady=10)

    # Create and pack the control panel.
    control_panel = ControlPanel(root, burst_command=dummy_burst_command, restart_command=dummy_restart_command)
    control_panel.pack(pady=5)

    # Create and pack the status label.
    status_label = StatusLabel(root, text="Status: Ready")
    status_label.pack(pady=5)

    # Test updating a specific cell (e.g., top-left cell).
    test_state = {
        "inquired": True,
        "color": "red",
        "probability": 1.00
    }
    grid_frame.cells[0][0].update_state(test_state["inquired"], test_state["color"], test_state["probability"])

    root.mainloop()

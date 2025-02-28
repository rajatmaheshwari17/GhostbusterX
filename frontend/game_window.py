"""
game_window.py

This module defines the GameWindow class which sets up and manages the main
game window for the Ghostbuster game using Tkinter. The window contains a 10x10 grid
of buttons representing cells, a control panel with a Burst Mode button and a Restart Game button,
and a status label. The GameWindow class interacts with the backend game logic to process
inquiries, update cell colors/probabilities, and handle burst mode.
"""

import tkinter as tk
from tkinter import messagebox
from backend.game_logic import Game

GRID_SIZE = 10  # 10x10 grid

class GameWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Ghostbuster Game")

        # Store grid size here so we can reference self.GRID_SIZE below
        self.GRID_SIZE = GRID_SIZE

        # Initialize backend game logic
        self.game = Game()

        # 2D list to store button references corresponding to grid cells
        self.buttons = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]

        # Set up the UI (build grid, control panel, etc.)
        self.setup_ui()

        # Immediately update the UI so we see initial probabilities
        self.update_ui()

    def setup_ui(self):
        # Frame for the game grid
        self.grid_frame = tk.Frame(self.master)
        self.grid_frame.pack(padx=10, pady=10)

        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                btn = tk.Button(
                    self.grid_frame,
                    text="",
                    width=8,
                    height=4,
                    command=lambda row=i, col=j: self.cell_clicked(row, col)
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                self.buttons[i][j] = btn

        # Frame for control buttons
        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(pady=10)

        self.burst_button = tk.Button(
            self.control_frame,
            text="Burst Mode",
            command=self.activate_burst_mode
        )
        self.burst_button.grid(row=0, column=0, padx=5)

        self.restart_button = tk.Button(
            self.control_frame,
            text="Restart Game",
            command=self.restart_game
        )
        self.restart_button.grid(row=0, column=1, padx=5)

        # Status label for game messages
        self.status_label = tk.Label(
            self.master,
            text="Inquiry Mode | Ghost moves left: " + str(self.game.ghost.moves_left)
        )
        self.status_label.pack(pady=5)

    def cell_clicked(self, row, col):
        """
        Handles a click on a grid cell.
        In inquiry mode, processes the inquiry; in burst mode, attempts to catch the ghost.
        """
        if self.game.burst_mode:
            # Burst mode: one attempt to catch the ghost
            caught = self.game.burst_mode_attempt(row, col)
            self.update_ui()
            if caught:
                messagebox.showinfo("Result", "Burst mode success! You caught the ghost!")
            else:
                messagebox.showerror("Result", "Burst mode failed. You lost!")
            self.disable_grid()
        else:
            # Inquiry mode
            ghost_moved = self.game.inquire_cell(row, col)
            self.update_ui()
            if ghost_moved:
                messagebox.showinfo("Info", "The ghost sensed you and moved!")
            self.status_label.config(text="Inquiry Mode | Ghost moves left: " + str(self.game.ghost.moves_left))

    def activate_burst_mode(self):
        """
        Activates burst mode so the next cell click is a one-chance ghost catch.
        """
        if not self.game.burst_mode:
            self.game.switch_to_burst_mode()
            self.status_label.config(text="Burst Mode Activated: Click on the ghost's location!")
        else:
            messagebox.showinfo("Info", "Burst Mode is already activated!")

    def disable_grid(self):
        """Disables all cell buttons after a burst mode attempt."""
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                self.buttons[i][j].config(state=tk.DISABLED)

    def update_ui(self):
        """
        Fetch the game status and update the grid.
        We ALWAYS display the probability for each cell, even if it's not inquired.
        """
        game_status = self.game.game_status()
        grid_state = game_status["grid"]  # A 2D list of cell info dicts

        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                cell_info = grid_state[i][j]
                color = cell_info["color"]          # "red", "orange", "green", or "neutral"
                prob = cell_info["probability"]     # e.g. 0.00 to 1.00

                # Map logical color to button background color
                if color == "red":
                    bg_color = "red"
                elif color == "orange":
                    bg_color = "orange"
                elif color == "green":
                    bg_color = "green"
                else:
                    bg_color = "SystemButtonFace"  # default button color

                # Always display the probability (2 decimals)
                text_value = f"{prob:.2f}"

                # Update the button
                self.buttons[i][j].config(bg=bg_color, text=text_value)

    def restart_game(self):
        """
        Resets the game by reinitializing the backend game logic, re-enabling all cells,
        and updating the UI accordingly.
        """
        self.game = Game()
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                self.buttons[i][j].config(state=tk.NORMAL)
        self.status_label.config(text="Inquiry Mode | Ghost moves left: " + str(self.game.ghost.moves_left))
        self.update_ui()

# For testing independently:
if __name__ == "__main__":
    root = tk.Tk()
    app = GameWindow(root)
    root.mainloop()

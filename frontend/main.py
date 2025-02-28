"""
main.py

This file implements the frontend for the ghostbuster game using Tkinter.
It creates a 10x10 grid where each cell is a clickable button that updates
its color and probability based on the game logic.
A control panel provides a Burst Mode button (one chance to catch the ghost)
and a Restart Game button.
"""

import tkinter as tk
from tkinter import messagebox
from backend.game_logic import Game

GRID_SIZE = 10  # 10x10 grid

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghostbuster Game")
        # Initialize the backend game logic
        self.game = Game()
        # Create a 2D list to store Button references for grid cells
        self.buttons = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.create_widgets()
        self.update_ui()

    def create_widgets(self):
        # Frame for the grid
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(padx=10, pady=10)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                # Each button represents a cell; clicking calls on_cell_click with its row and col.
                btn = tk.Button(
                    self.grid_frame,
                    text="",
                    width=8,
                    height=4,
                    command=lambda row=i, col=j: self.on_cell_click(row, col)
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                self.buttons[i][j] = btn

        # Control frame for extra buttons
        self.control_frame = tk.Frame(self.root)
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

        # Label to display game status
        self.status_label = tk.Label(self.root, text="Inquiry Mode | Ghost moves left: " + str(self.game.ghost.moves_left))
        self.status_label.pack(pady=5)

    def on_cell_click(self, row, col):
        """
        Handles a click on a cell. In normal inquiry mode, it processes the cell
        inquiry. In burst mode, it attempts a burst mode catch.
        """
        if self.game.burst_mode:
            # Process burst mode: one chance to catch the ghost.
            caught = self.game.burst_mode_attempt(row, col)
            self.update_ui()
            if caught:
                messagebox.showinfo("Result", "Burst mode success! You caught the ghost!")
            else:
                messagebox.showerror("Result", "Burst mode failed. You lost!")
            self.disable_grid()
        else:
            # In inquiry mode, process the cell inquiry.
            ghost_moved = self.game.inquire_cell(row, col)
            self.update_ui()
            if ghost_moved:
                messagebox.showinfo("Info", "The ghost sensed you and moved!")
            # Update the status label with ghost moves left.
            self.status_label.config(text="Inquiry Mode | Ghost moves left: " + str(self.game.ghost.moves_left))

    def activate_burst_mode(self):
        """
        Activates burst mode. The next cell click will attempt to catch the ghost.
        """
        if not self.game.burst_mode:
            self.game.switch_to_burst_mode()
            self.status_label.config(text="Burst Mode Activated: Click on the ghost's location!")
        else:
            messagebox.showinfo("Info", "Burst Mode is already activated!")

    def disable_grid(self):
        """Disables all cell buttons."""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.buttons[i][j].config(state=tk.DISABLED)

    def update_ui(self):
        """
        Retrieves the current game state and updates each button's background color
        and text (to display the probability, if the cell has been inquired).
        """
        game_status = self.game.game_status()
        grid_state = game_status["grid"]

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                cell_info = grid_state[i][j]
                color = cell_info["color"]
                prob = cell_info["probability"]
                inquired = cell_info["inquired"]

                # Map cell color state to button background color.
                if color == "red":
                    bg_color = "red"
                elif color == "orange":
                    bg_color = "orange"
                elif color == "green":
                    bg_color = "green"
                else:
                    bg_color = "SystemButtonFace"  # default button color

                self.buttons[i][j].config(bg=bg_color)
                # Display probability if the cell has been inquired; otherwise, show empty text.
                if inquired:
                    self.buttons[i][j].config(text=f"{prob:.2f}")
                else:
                    self.buttons[i][j].config(text="")

    def restart_game(self):
        """
        Resets the game by creating a new Game instance, re-enabling all buttons,
        and updating the UI.
        """
        self.game = Game()
        self.status_label.config(text="Inquiry Mode | Ghost moves left: " + str(self.game.ghost.moves_left))
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.buttons[i][j].config(state=tk.NORMAL)
        self.update_ui()

def main():
    root = tk.Tk()
    gui = GameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
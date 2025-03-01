
# GhostbusterX

GhostbusterX is a Python-based Ghostbuster game that uses **Bayesian inference** with **fuzzy-likelihood** logic. Each time you click a cell to “inquire” about the ghost’s position, probabilities across the entire grid update dynamically—so even distant cells never truly drop to zero. The game also features **observational error**, distance-based color coding (red/orange/yellow/green), a **minimum probability floor** to avoid zeros, and optional ghost movement for an extra challenge.



## Features

1.  **Bayesian Updates**
    
    -   Each click triggers a Bayesian update, multiplying prior probabilities by a likelihood table based on observed color and distance.
    -   A small **floor** (e.g., `1e-5`) ensures probabilities never become exactly zero.
2.  **Observational Error / Fuzzy Likelihood**
    
    -   Seeing “orange” doesn’t always mean the ghost is exactly 1 cell away; there’s a chance it’s 0, 2, or even >2 cells away.
    -   This partial-likelihood approach keeps the entire grid relevant.
3.  **Distance-Based Colors**
    
    -   Red (distance 0), Orange (distance 1), Yellow (distance 2), Green (distance >2).
    -   Easily customizable in both logic and UI.
4.  **Ghost Movement (Optional)**
    
    -   The ghost can move if a threshold of neighbors is inquired.
    -   This adds a dynamic element, requiring repeated inference.
5.  **Minimum Probability Floor**
    
    -   Ensures no cell probability becomes 0.0, allowing “revival” if new evidence favors it.


## Installation

1.  **Clone or Download** this repository:
    
    ```bash
    git clone git@github.com:rajatmaheshwari17/GhostbusterX.git
    cd GhostbusterX
    
    ```
    
2.  **Install Dependencies** (for Linux):
    
    ```bash
    sudo apt-get install python3-tk    
    ```
    
   
    
3.  **Run** the game:
    
    ```bash
    python3 -m frontend.game_window
    
    ```
    
    _(Make sure you have Python 3 installed and you are in the root directory.)_
    



## How to Play

1.  **Grid Setup**
    
    -   A 6×6 (or 10×10) grid of cells. Each cell starts with equal probability.
2.  **Inquiries (Clicks)**
    
    -   Click a cell to see if the ghost is at distance 0 (red), 1 (orange), 2 (yellow), or >2 (green).
    -   Each observation has some **chance** of being “wrong,” so the game updates probabilities using a **fuzzy-likelihood** table.
3.  **Bayesian Probability Updates**
    
    -   The code multiplies each cell’s prior by `P(observed_color | distance)`, then normalizes.
    -   A probability floor ensures no cell hits 0.0 exactly.
4.  **Ghost Movement**
    
    -   If enough neighbors of a cell are inquired (e.g., ≥ 75%), the ghost may move to another location.
    -   You can disable or tweak this in `game_logic.py` if you want a simpler game.
5.  **Burst Mode**
    
    -   Switch to burst mode for a **single** guess to catch the ghost. If correct, you win instantly; if not, you lose.



## Observational Error (Fuzzy Logic)

In `bayes_updates.py`, we use a table of likelihoods to handle potential observational error. For example:

| Distance | Red  | Orange | Yellow | Green |
|----------|------|--------|--------|-------|
| 0        | 0.80 | 0.10   | 0.05   | 0.05  |
| 1        | 0.10 | 0.70   | 0.10   | 0.10  |
| 2        | 0.05 | 0.10   | 0.70   | 0.15  |
| >2       | 0.05 | 0.05   | 0.10   | 0.80  |

- **Distance** is the Chebyshev distance between the ghost’s actual position and the clicked cell.
- **Color** is what the player observes:
  - **Red** (distance 0)  
  - **Orange** (distance 1)  
  - **Yellow** (distance 2)  
  - **Green** (distance >2)  

Each cell shows the probability \( P(\text{Color} \mid \text{Distance}) \). Notice no scenario is 100% or 0%, so the entire grid gets updated after each inquiry, not just a local region. This approach allows for “wrong” observations (e.g., distance=0 but you see orange 10% of the time). 



## Customization

-   **Grid Size**: Change `GRID_SIZE` in `game_logic.py` or `grid.py`.
-   **Likelihood Table**: Adjust partial probabilities in `bayes_updates.py` to make the game easier or harder.
-   **Min Probability Floor**: In `bayes_updates.py`, set `min_prob` to control how close to zero probabilities can get.
-   **Ghost Moves**: Increase `moves_left` for the ghost if you want a more dynamic game.

----------
_This README is a part of the GhostbusterX Project by Rajat Maheshwari._

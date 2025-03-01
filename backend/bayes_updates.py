"""
bayes_updates.py

Implements a Bayesian update with observational error (fuzzy logic).
If distance=0, there's an 80% chance you observe "red", 10% "orange", etc.
If distance=1, 70% "orange", etc.
If distance=2, 70% "yellow".
If distance>2, 80% "green".

You can tweak these numbers as desired.
"""

def apply_bayes_update(grid, clicked_row, clicked_col, observed_color):
    """
    For each cell in the grid, compute the Chebyshev distance to (clicked_row, clicked_col),
    then use the probability table P(observed_color | distance) to get the likelihood.

    Multiply each cell's prior by that likelihood, then normalize across the grid.
    """

    # 1) Define the observational error table:
    #    P(color | distance) for distance=0,1,2,>2
    #    You can store these in a dict for easy reference.

    # distances we handle explicitly: 0, 1, 2, >2
    # colors: red, orange, yellow, green
    # We'll define a helper function that returns P(observed_color | distance).

    def observation_likelihood(distance, color):
        if distance == 0:
            # ghost is exactly in clicked cell
            if color == "red":
                return 0.80
            elif color == "orange":
                return 0.10
            elif color == "yellow":
                return 0.05
            else:  # green
                return 0.05

        elif distance == 1:
            if color == "red":
                return 0.10
            elif color == "orange":
                return 0.70
            elif color == "yellow":
                return 0.10
            else:  # green
                return 0.10

        elif distance == 2:
            if color == "red":
                return 0.05
            elif color == "orange":
                return 0.10
            elif color == "yellow":
                return 0.70
            else:  # green
                return 0.15

        else:
            # distance > 2
            if color == "red":
                return 0.05
            elif color == "orange":
                return 0.05
            elif color == "yellow":
                return 0.10
            else:  # green
                return 0.80

    # 2) Calculate unnormalized posteriors for each cell
    unnormalized = []
    for cell in grid.all_cells():
        prior = cell.probability

        # Chebyshev distance
        dist = max(abs(cell.row - clicked_row), abs(cell.col - clicked_col))

        # Likelihood from our table
        like = observation_likelihood(dist, observed_color)

        unnormalized_val = prior * like
        unnormalized.append(unnormalized_val)

    # 3) Normalize
    total = sum(unnormalized)
    if total < 1e-12:
        print("[Warning] All probabilities ended up near zero. Reset to uniform.")
        uniform = 1.0 / (grid.size * grid.size)
        idx = 0
        for cell in grid.all_cells():
            cell.probability = uniform
            idx += 1
        return
    else:
        idx = 0
        for cell in grid.all_cells():
            cell.probability = unnormalized[idx] / total
            idx += 1

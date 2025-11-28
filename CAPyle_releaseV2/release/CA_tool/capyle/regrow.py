from . import terrain_cell as tc
from enum import Enum
import numbers
import random
import math
import numpy as np

#regrowth rat table
#usage e.g. REGROWTH_RATE.get(tc.TerrainType.CHAPARRAL, 0.0)
REGROWTH_RATE = {
    tc.TerrainType.CHAPARRAL: 0.02,
    tc.TerrainType.DENSE_FOREST: 0.01,
    tc.TerrainType.CANYON_SCRUBLAND: 0.015,
    tc.TerrainType.LAKE: 0.0,
    tc.TerrainType.SOURCE: 0.0,
    tc.TerrainType.TOWN: 0.0
}

def regrow_transition_func(
    grid,
    neighbour_states,
    neighbour_counts,
    time_step
):

    new_grid = np.empty_like(grid)
    rows, cols = grid.shape

    RESPROUT_CHANCE_MULTIPLIER = 0.5

    neighbour_offsets = [
        (-1, -1),   # NW
        ( 0, -1),   # N
        ( 1, -1),   # NE
        (-1,  0),   # W
        ( 1,  0),   # E
        (-1,  1),   # SW
        ( 0,  1),   # S
        ( 1,  1)    # SE
    ]

    for x in range(rows):
        for y in range(cols):
            old_cell = grid[x, y]

            if old_cell is None:
                new_grid[x, y] = None
                continue

            if old_cell.type in (
                tc.TerrainType.LAKE,
                tc.TerrainType.SOURCE,
                tc.TerrainType.TOWN
            ):
                new_grid[x, y] = old_cell
                continue

            # Copy current cell for modification
            new_cell = old_cell.copy()

            # If cell is burnt attempt regrowth
            if old_cell.burnt:

                # Early resprout chance based on seed bank under soil
                if time_step < 3:
                    if random.random() < (
                        REGROWTH_RATE.get(old_cell.type, 0.0)
                        * RESPROUT_CHANCE_MULTIPLIER
                    ):
                        new_cell.burnt = False
                        new_grid[x, y] = new_cell
                        continue

                # Seed spread from neighbours
                if 1 <= x < rows - 1 and 1 <= y < cols - 1:

                    for idx, ns_array in enumerate(neighbour_states):

                        neighbour = ns_array[x, y]

                        if neighbour is None:
                            continue

                        # avoid int labels
                        if isinstance(neighbour, numbers.Integral):
                            continue

                        # Only natural vegetation spreads
                        if neighbour.burnt:
                            continue

                        neighbour_type = neighbour.type

                        if neighbour_type not in (
                            tc.TerrainType.CHAPARRAL,
                            tc.TerrainType.DENSE_FOREST,
                            tc.TerrainType.CANYON_SCRUBLAND
                        ):
                            continue

                        spread_prob = REGROWTH_RATE.get(neighbour_type, 0.0)

                        # Direction effects (wind)
                        dx, dy = neighbour_offsets[idx]
                        angle = (math.degrees(math.atan2(-dy, dx)) + 360) % 360

                        # prevailing wind is south (time scale is large enough to assert south wind dominance)
                        wind_effect = 1.3 if 90 < angle <= 180 else 1

                        slope_effect = old_cell.get_slope_effect(neighbour.elevation)

                        prob = spread_prob * wind_effect * slope_effect
                        prob = max(0.0, min(prob, 1.0))

                        # Apply seed spread
                        if random.random() < prob:
                            new_cell.type = neighbour_type
                            new_cell.burnt = False
                            break

            # add updated cell to grid
            new_grid[x, y] = new_cell

    return new_grid, False

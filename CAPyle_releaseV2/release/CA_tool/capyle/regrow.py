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

    neighbour_offsets = [
        (-1,-1), (0,-1), (1,-1),
        (-1,0),           (1,0),
        (-1,1),  (0,1),   (1,1)
    ]

    for x in range(rows):
        for y in range(cols):
            old_cell = grid[x, y]
            new_cell = old_cell.copy()

            if old_cell.burnt:
                if time_step < 2:
                    prob_resprout = random.random()
                    if prob_resprout < (REGROWTH_RATE.get(old_cell.type, 0.0) * 2):
                        new_cell.burnt = False
                        continue

                #regrow from seed spread
                for idx, ns_array in enumerate(neighbour_states):
                    neighbour = ns_array[x, y]
                    if neighbour is not None and not isinstance(neighbour, numbers.Integral):
                        dx, dy = neighbour_offsets[idx]

                        spread_prob = REGROWTH_RATE.get(neighbour.type, 0.0)

                        spread_dir = (math.degrees(math.atan2(dy, dx)) - 270 + 360) % 360

                        if spread_dir > 90 and spread_dir <= 270:
                            wind_effect = 1.2
                        else:
                            wind_effect = 1

                        slope_effect = old_cell.get_slope_effect(neighbour.elevation)

                        prob = (1 - (1 - spread_prob) ** wind_effect) * slope_effect
                        prob = max(0.0, min(prob, 1.0))

                        if random.random() < prob:
                            new_cell.type = old_cell.type
                            new_cell.burnt = False
                            break 

            new_grid[x, y] = new_cell

    return new_grid, False #(Stopping condition is always false for this function)
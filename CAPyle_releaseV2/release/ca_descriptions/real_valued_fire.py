# Name: Fire in a Real Domain
# Dimensions: 2

# --- Set up executable path, do not edit ---
import copy
import math
import numbers
import random
import sys
import inspect
from functools import partial

this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from matplotlib import colors
from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np
from CA_tool.capyle.terrain_cell import TerrainCell, TerrainType, cell_to_state_index
from CA_tool.capyle.wind import Wind

def transition_func(
    grid, 
    neighbour_states, 
    neighbour_counts, 
    wind_distribution: Wind, 
    water_dropping_plan=None
):
    rows, cols = grid.shape

    ignite_mask = np.zeros_like(grid, dtype=bool)

    neighbor_offsets = [(-1,-1), (0,-1), (1,-1),
                    (-1,0),           (1,0),
                    (-1,1),  (0,1),   (1,1)]

    for x in range(rows):
        for y in range(cols):
            cell = grid[x, y]

            if cell.burning:
                continue

            for idx, ns_array in enumerate(neighbour_states):
                if x < ns_array.shape[0] and y < ns_array.shape[1]:
                    neighbor = ns_array[x, y]
                    if neighbor is not None and not isinstance(neighbor, numbers.Integral) and neighbor.burning:
                        dx, dy = neighbor_offsets[idx]

                        fire_dir = (math.degrees(math.atan2(dy, dx)) + 360) % 360

                        wind_prob = wind_distribution.fire_spread_contribution(fire_dir)

                        prob = 0.05 + (1 - 0.05) * wind_prob
                        prob = min(prob, 1.0)

                        if random.random() < prob:
                            ignite_mask[x, y] = True
                            break 

    for x in range(rows):
        for y in range(cols):
            cell = grid[x, y]

            if cell.burning:
                cell.burn()
            elif ignite_mask[x, y]:
                cell.ignite()
            else:
                cell.regenerate()

    return grid

def setup(args, wind_direction):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Real Fire"
    config.dimensions = 2
    config.states = (1,2,3,4,5,6)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # config.state_colors = [(0,0,0),(1,1,1)]
    # config.num_generations = 150
    # config.grid_dims = (200,200)

    # ----------------------------------------------------------------------

    grid = np.empty((200,200), TerrainCell)
    for x in range(0,200):
        for y in range(0,200):
            grid[x,y] = TerrainCell(
                TerrainType.CHAPARRAL,
                regen_rate=random.random() * (1/2880 - 1/5760) + 1/5760,
                burn_rate=random.random() * (1/24 - 1/168) + 1/168
            )

    for x in range(20,30):
        for y in range(20,80):
            grid[x,y] = TerrainCell(
                TerrainType.DENSE_FOREST,
                regen_rate=random.random() * (1/8640 - 1/12960) + 1/12960,
                burn_rate=random.random() * (1/480 - 1/720) + 1/720
            )
    
    for x in range(30,100):
        for y in range(20,50):
            grid[x,y] = TerrainCell(
                TerrainType.DENSE_FOREST,
                regen_rate=random.random() * (1/8640 - 1/12960) + 1/12960,
                burn_rate=random.random() * (1/480 - 1/720) + 1/720
            )

    for x in range(100,140):
        for y in range(20,100):
            grid[x,y] = TerrainCell(
                TerrainType.DENSE_FOREST,
                regen_rate=random.random() * (1/8640 - 1/12960) + 1/12960,
                burn_rate=random.random() * (1/480 - 1/720) + 1/720
            )

    for x in range(40,130):
        for y in range(140,150):
            grid[x,y] = TerrainCell(
                TerrainType.CANYON_SCRUBLAND,
                regen_rate=random.random() * (1/720 - 1/1440) + 1/1440,
                burn_rate=random.random() * (1/6 - 1/12) + 1/12
            )

    for x in range(40,80):
        for y in range(70,80):
            grid[x,y] = TerrainCell(
                TerrainType.LAKE
            )

    for x in range(160,170):
        for y in range(100,160):
            grid[x,y] = TerrainCell(
                TerrainType.LAKE
            )

    for x in range(176,186):
        for y in range(56,66):
            grid[x,y] = TerrainCell(
                TerrainType.TOWN
            )
    
    grid[0,20] = TerrainCell(
        TerrainType.SOURCE,
        burning = True
    )

    config.initial_grid = grid
    config.dtype = TerrainCell
    
    config.state_index_function = cell_to_state_index

    config.states = list(range(len(TerrainType) * 2))

    def type_to_colour(type: TerrainType) -> str:
        color_map = {
            TerrainType.CHAPARRAL: "#bfbf00",
            TerrainType.CANYON_SCRUBLAND: "#feff00",
            TerrainType.DENSE_FOREST: "#4f6227",
            TerrainType.LAKE: "#3db0f0",
            TerrainType.SOURCE: "#ffffff",
            TerrainType.TOWN: "#000000",
        }

        return color_map.get(type, "#000000")

    state_colors = []
    for terrain in TerrainType:
        base_rgb = colors.to_rgb(type_to_colour(terrain))
        fire_rgb = (1.0, 0.0, 0.0) 
        state_colors.append(base_rgb)
        state_colors.append(fire_rgb)

    config.state_colors = state_colors

    config.wrap = False
    config.num_generations = 100
    config.timeline_path = f"wd_{wind_direction}_timeline"

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main(wind_speed = 13.892, direction = 0, k = 37.284, c = 14.778):
    # Open the config object
    config = setup(sys.argv[1:], direction)

    wind = Wind(wind_speed, direction, k, c)

    # Create grid object
    grid = Grid2D(config, partial(transition_func, wind_distribution=wind))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
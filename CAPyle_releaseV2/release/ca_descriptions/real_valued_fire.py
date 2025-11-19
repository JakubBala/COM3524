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

import os
import json
import CA_tool.capyle as capyle_module
water_json_path = os.path.join(
    os.path.dirname(capyle_module.__file__),
    "waterdrops.json"
)
# ---

from matplotlib import colors
from CA_tool.capyle.ca import Grid2D
import CA_tool.capyle.utils as utils
import numpy as np
from CA_tool.capyle.terrain_cell import TerrainCell, TerrainType, cell_to_state_index
from CA_tool.capyle.wind import Wind

def transition_func(
    grid, 
    neighbour_states, 
    neighbour_counts, 
    wind_distribution: Wind, 
    water_dropping_plan=None,
    step_num=0
):
    
    rows, cols = grid.shape

    ignite_mask = np.zeros_like(grid, dtype=bool)

    neighbor_offsets = [(-1,-1), (0,-1), (1,-1),
                    (-1,0),           (1,0),
                    (-1,1),  (0,1),   (1,1)]

    water_mask = np.zeros((rows, cols), dtype=bool)
    if water_dropping_plan is not None:
        step_key = str(step_num)
        if step_key in water_dropping_plan:
            # print(f"Step {step_num}: Water drops at coordinates:")
            for (x, y) in water_dropping_plan[step_key]:
                x, y = int(x), int(y)
                if 0 <= x < rows and 0 <= y < cols:
                    water_mask[x, y] = True
                    print(f"  ({x}, {y})")

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

                        fire_dir = (math.degrees(math.atan2(dy, dx)) - 270 + 360) % 360

                        wind_prob = wind_distribution.fire_spread_contribution(fire_dir)

                        prob = 0.05 + (1 - 0.05) * wind_prob
                        prob = min(prob, 1.0)

                        if random.random() < prob:
                            ignite_mask[x, y] = True
                            break 

    for x in range(rows):
        for y in range(cols):
            cell = grid[x, y]

            # remove waterdropped effect after the dropping step
            if(cell.waterdropped):
                cell.waterdropped = False

            elif water_mask[x, y]:
                cell.drop_water()

            elif cell.burning:
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

    config.states = list(range(len(TerrainType) * 3))

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
        waterdrop_rgb = (0.0, 0.0, 1.0)
        state_colors.append(base_rgb)
        state_colors.append(fire_rgb)
        state_colors.append(waterdrop_rgb)

    config.state_colors = state_colors

    config.wrap = False
    # config.num_generations = num_iterations
    config.timeline_path = f"wd_{wind_direction}_timeline"

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main(wind_speed = 13.892, direction = 0, k = 37.284, c = 14.778):
    # Open the config object
    config = setup(sys.argv[1:], direction)

    wind = Wind(wind_speed, direction, k, c)

    #--- LOAD WATER PLAN JSON---

    load_water_plan = True
    
    water_plan = None

    if(load_water_plan):
        with open(water_json_path, "r") as f:
            water_plan = json.load(f)

    # Create grid object
    grid = Grid2D(config, partial(transition_func, wind_distribution=wind, water_dropping_plan=water_plan))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
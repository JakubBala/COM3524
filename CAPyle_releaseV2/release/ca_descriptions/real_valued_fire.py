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

from matplotlib import colors
from CA_tool.capyle.ca import Grid2D
import CA_tool.capyle.utils as utils
import numpy as np
from CAPyle_releaseV2.release.CA_tool.capyle.terrain_cell import TerrainCell, TerrainType, cell_to_state_index
from CAPyle_releaseV2.release.CA_tool.capyle.wind import Wind
from CAPyle_releaseV2.release.CA_tool.capyle.regrow import regrow_transition_func, REGROWTH_RATE

EDGE_W = 0.785398
CORNER_W = 0.214601
EDGE_W_N  = 1.0
CORNER_W_N = CORNER_W / EDGE_W 

def transition_func(
    grid, 
    neighbour_states, 
    neighbour_counts, 
    time_step,
    wind_distribution: Wind, 
    water_dropping_plan=None,
    config=None
):
    new_grid = np.empty_like(grid)    
    rows, cols = grid.shape

    neighbour_offsets = [
        (-1,-1), (0,-1), (1,-1),
        (-1,0),           (1,0),
        (-1,1),  (0,1),   (1,1)
    ]

    drops = set(tuple(coord) for coord in water_dropping_plan.get(str(time_step), []))

    town_ignited = False
    for x in range(rows):
        for y in range(cols):
            old_cell = grid[x, y]
            new_cell = old_cell.copy()

            if (x, y) in drops:
                new_cell.drop_water()
            elif old_cell.waterdropped:
                new_cell.waterdropped = False

            if not old_cell.burning and not old_cell.burnt:
                for idx, ns_array in enumerate(neighbour_states):
                    neighbour = ns_array[x, y]
                    if neighbour is not None and not isinstance(neighbour, numbers.Integral) and neighbour.burning:
                        dx, dy = neighbour_offsets[idx]

                        ignition_source = neighbour.type
                        ignition_prob = old_cell.get_ignition_prob(ignition_source)

                        moisture = old_cell.moisture
                        moisture_effect = 1 - 2.59*moisture + 5.11*moisture**2 - 3.52*moisture**3
                        moisture_effect = max(0.0, min(1.0, moisture_effect))

                        fire_dir = (math.degrees(math.atan2(dy, dx)) - 270 + 360) % 360

                        wind_prob = wind_distribution.fire_spread_contribution(fire_dir)

                        slope_effect = old_cell.get_slope_effect(neighbour.elevation)

                        prob = (1 - (1 - ignition_prob) ** wind_prob) * moisture_effect * slope_effect
                        prob = max(0.0, min(prob, 1.0))

                        if random.random() < prob:
                            new_cell.ignite()
                            if new_cell.type == TerrainType.TOWN:
                                town_ignited = True
                                if config is not None and getattr(config, "town_ignition_step", None) is None:
                                    config.town_ignition_step = time_step
                            break 
            
            if old_cell.burning:
                new_cell.burn()

            new_grid[x, y] = new_cell

    return new_grid, town_ignited

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
    
    #If user chooses to run regrowth simulation, set all cells to burnt initially
    if getattr(config, "run_regrow", False):
        cells_burnt = True
    else:
        cells_burnt = False

    grid = np.empty((200,200), TerrainCell)
    for x in range(0,200):
        for y in range(0,200):
            grid[x,y] = TerrainCell(
                TerrainType.CHAPARRAL,
                burnt = cells_burnt
            )

    # small flick at the top(north) of forest
    for x in range(20,30):
        for y in range(20,80):
            grid[x,y] = TerrainCell(
                TerrainType.DENSE_FOREST,
                burnt = cells_burnt
            )
    
    # tall trunk of forest
    for x in range(30,100):
        for y in range(20,50):
            grid[x,y] = TerrainCell(
                TerrainType.DENSE_FOREST,
                burnt = cells_burnt
            )

    # large south block of forest
    for x in range(100,140):
        for y in range(20,100):
            grid[x,y] = TerrainCell(
                TerrainType.DENSE_FOREST,
                burnt = cells_burnt
            )

    # CANYON
    canyon_x_start = 40
    canyon_x_end   = 130
    canyon_depth   = -100
    length = canyon_x_end - canyon_x_start
    desc_pct = 0.1   # % descent
    asc_pct  = 0.1   # % ascent
    flat_pct = 1 - desc_pct - asc_pct  # middle %
    for x in range(40,130):

        # Normalised position across canyon (0.0 → 1.0)
        t = (x - canyon_x_start) / length

        # Compute elevation using piecewise function
        elev = 0.0
        if t < desc_pct:
            # DESCENDING section (0 → depth)
            elev = 0 + (t / desc_pct) * (canyon_depth - 0)

        elif t < desc_pct + flat_pct:
            # FLAT canyon floor
            elev = canyon_depth

        else:
            # ASCENDING section (depth → 0)
            t2 = (t - (desc_pct + flat_pct)) / asc_pct
            elev = canyon_depth + t2 * (0 - canyon_depth)

        for y in range(140,150):
            grid[x,y] = TerrainCell(
                TerrainType.CANYON_SCRUBLAND,
                burnt = cells_burnt,
                elevation=elev
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
    
    # add ignition sources if enabled
    if getattr(config, "power_plant_enabled", False) and not cells_burnt:
        grid[0,20] = TerrainCell(TerrainType.SOURCE, burning=True)
    if getattr(config, "incinerator_enabled", False) and not cells_burnt:
        grid[0,199] = TerrainCell(TerrainType.SOURCE, burning=True)

    # add intervention 1 - extended forest left (if enabled)
    if getattr(config, "intervention_1_enabled", False):
        for x in range(100, 140):
            for y in range(0, 20):
                grid[x,y] = TerrainCell(
                    TerrainType.DENSE_FOREST,
                    burnt = cells_burnt
                )

    # add intervention 2 - extended forest down (if enabled)
    if getattr(config, "intervention_2_enabled", False):
        for x in range(140, 160):
            for y in range(20, 100):
                grid[x,y] = TerrainCell(
                    TerrainType.DENSE_FOREST,
                    burnt = cells_burnt
                )

    # if both forest interventions are enabled - make square
    if getattr(config, "intervention_1_enabled", False) and getattr(config, "intervention_2_enabled", False):
        for x in range(140, 160):
            for y in range(0, 20):
                grid[x,y] = TerrainCell(
                    TerrainType.DENSE_FOREST,
                    burnt = cells_burnt
                )

    # add intervention 3 - flood the canyon (if enabled)
    if getattr(config, "intervention_3_enabled", False):
        for x in range(40,130):
            for y in range(140,150):
                grid[x,y] = TerrainCell(
                    TerrainType.LAKE
                )

    config.initial_grid = grid
    config.dtype = TerrainCell
    config.town_ignition_step = None
    
    config.state_index_function = cell_to_state_index

    config.states = list(range(len(TerrainType) * 4))  # 4 states per terrain type

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
        burnt_rgb = (0.2, 0.2, 0.2)
        state_colors.append(base_rgb)
        state_colors.append(fire_rgb)
        state_colors.append(waterdrop_rgb)
        state_colors.append(burnt_rgb)

    config.state_colors = state_colors

    config.wrap = False
    # config.num_generations = num_iterations
    config.timeline_path = f"wd_{wind_direction}_timeline"

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main(
    wind_speed = 13.892, 
    direction = 0, 
    k = 37.284, 
    c = 14.778,
    water_plan_path = None,
    water_dropping_plan = None
):
    # Open the config object
    config = setup(sys.argv[1:], direction)

    wind = Wind(wind_speed, direction, k, c)
    
    if water_plan_path is not None and water_dropping_plan is None:
        with open(water_plan_path, "r") as f:
            water_dropping_plan = json.load(f)

    # Choose which transition function to use based on whether regrowth is enabled.
    if getattr(config, "run_regrow", False):
        grid = Grid2D(
            config, 
            partial(
                regrow_transition_func 
            )
        )
    else:
        grid = Grid2D(
            config, 
            partial(
                transition_func, 
                wind_distribution=wind, 
                water_dropping_plan=water_dropping_plan,
                config=config
            )
        )

    # Run the CA, save grid state every generation to timeline
    timeline, time_step = grid.run()
    print(f"Stopping Condition met at time {time_step}")

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main(water_plan_path=water_json_path)
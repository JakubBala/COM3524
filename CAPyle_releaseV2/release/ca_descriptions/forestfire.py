# Name: Conway's game of life
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np

states = (0, 1, 2, 3, 4,
        10, 11, 12, 13, 14,
        20, 21, 22, 23, 24)

col_chaparral = (0.98, 0.79, 0)
col_denseforest = (0.06, 0.37, 0.02)
col_lake = (0.207, 0.86, 0.98)
col_canyon = (0.98, 0.98, 0)
col_firesource = (0,0,0)
col_onfire = (1,0,0)
col_charred = (0.62, 0.56, 0.56)


state_colours = [col_chaparral, col_denseforest, col_lake, col_canyon, col_firesource,
                col_onfire, col_onfire, col_onfire, col_onfire, col_onfire, 
                col_charred, col_charred, col_charred, col_charred, col_charred]


def transition_func(grid, neighbourstates, neighbourcounts):

    #chaparral = 0
    #dense forest = 1
    #lake = 2
    #canyon = 3
    #fire source = 4
    #on fire = + 10
    #burned = + 20

    flammable = {
        0: True,   # chaparral
        1: True,   # dense forest
        2: False,  # lake
        3: True,   # canyon
        4: True    # fire source (can also ignite if not already)
    }

    state_idx = {s: i for i, s in enumerate(states)}
    
    # --- Identify neighbours that are burning ---
    # Burning states are 10–19
    burning_neighbour_total = np.zeros_like(grid, dtype=int)
    for s in range(10, 15):
        burning_neighbour_total += neighbourcounts[state_idx[s]].astype(int)

    # --- Extract base terrain ---
    base = (grid % 10).astype(int)

    # --- Flammability mask ---
    flammable_mask = np.vectorize(lambda b: flammable[b])(base)

    # --- Rule 1: Burning cells stay burning ---
    still_burning = (grid >= 10) & (grid < 20)

    # --- Rule 2: Flammable cells next to fire ignite ---
    can_burn = (grid < 10) & flammable_mask
    ignite = can_burn & (burning_neighbour_total > 0)

    # --- Update grid in place ---
    # Cells that ignite become burning
    grid[ignite] = base[ignite] + 10
    # Burning cells remain burning
    grid[still_burning] = grid[still_burning]

    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Conway's game of life"
    config.dimensions = 2
    config.states = states
    config.wrap = False
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = state_colours
    # config.num_generations = 150
    # config.grid_dims = (200,200)

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    # Create grid object
    grid = Grid2D(config, transition_func)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()

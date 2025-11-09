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

    # convert dictionary to NumPy array for vectorized lookup
    # assumes states 0–4 exist
    flammable_arr = np.array([flammable[i] for i in range(max(flammable.keys()) + 1)])

    
    # copy grid to update in place (like Game of Life)
    new_grid = grid.copy()

    # Identify neighbours that are on fire
    on_fire_neighbour = ((neighbourstates >= 10) & (neighbourstates < 20)).any(axis=0)

    # extract base terrain (0–4)
    base = (grid % 10).astype(int)

    # --- RULE 1: Cells that ignite ---
    # cells that are below 10 are not burning/burned yet
    can_burn = (grid < 10) & flammable_arr[base]

    # cells that ignite if at least one neighbour is on fire
    ignite = can_burn & on_fire_neighbour

    # mark those as on fire (+10)
    new_grid[ignite] = base[ignite] + 10

    # --- RULE 2 (TEMP): Burning cells stay burning (no decay) ---
    # no need to change burning cells; just ensure they remain burning
    burning = (grid >= 10) & (grid < 20)
    new_grid[burning] = grid[burning]

    return new_grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Conway's game of life"
    config.dimensions = 2
    config.states = (0, 1, 2, 3, 4, 10, 11, 12, 13, 14, 20, 21, 22, 23, 24)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    chaparral = (0.98, 0.79, 0)
    denseforest = (0.06, 0.37, 0.02)
    lake = (0.207, 0.86, 0.98)
    canyon = (0.98, 0.98, 0)
    firesource = (0,0,0)
    onfire = (1,0,0)
    charred = (0.62, 0.56, 0.56)

    config.state_colors = [chaparral, denseforest, lake, canyon, firesource,
                        onfire, onfire, onfire, onfire, onfire, 
                        charred, charred, charred, charred, charred]
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

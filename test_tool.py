
from functools import partial
import inspect
import sys

import numpy as np

sys.path.append("/src")
sys.path.append("/src/CA_tool")
sys.path.append("/src/CAPyle_releaseV2/release")
sys.path.append("/src/CAPyle_releaseV2/release/CA_tool/capyle")
sys.path.append("/src/CAPyle_releaseV2/release/CA_tool/capyle/guicomponents")
sys.path.append("/src/CAPyle_releaseV2/release/CA_tool/capyle/ca")

from CAPyle_releaseV2.release.CA_tool.capyle.terrain_cell import TerrainType
from CAPyle_releaseV2.release.ca_descriptions.real_valued_fire import setup, transition_func
from CAPyle_releaseV2.release.CA_tool.capyle import utils
from CAPyle_releaseV2.release.CA_tool.capyle.ca.grid2d import Grid2D
from CAPyle_releaseV2.release.CA_tool.capyle.wind import Wind

def get_results(
    wind_speed = 13.892, 
    direction = 0, 
    k = 37.284, 
    c = 14.778, 
    water_dropping_plan = None, 
    timeline_path="timeline",
    num_iterations = 100,
    config_path="CAPyle_releaseV2/release/CA_tool/temp/config.pkl"
):
    """
    Run the fire simulation and compute:
      1) The iteration/time when fire first reaches a town.
      2) The fire coverage (fraction of burning cells) at that time.
    """

    args = [config_path]
    config = setup(args, direction, num_iterations)
    wind = Wind(wind_speed, direction, k, c)
    grid = Grid2D(config, partial(transition_func, wind_distribution=wind, water_dropping_plan=water_dropping_plan))

    timeline = grid.run()
    utils.save(timeline, config.timeline_path)

    time_fire_reaches_town = None
    coverage_at_time = 0.0

    for t, grid_state in enumerate(timeline):
        total_cells = grid_state.size
        burning_cells = np.sum(grid_state % 2 == 1)  # all odd numbers are "burning"
        town_cells = (grid_state == 10) | (grid_state == 11)

        if np.any(grid_state[town_cells] == 11):
            time_fire_reaches_town = t
            coverage_at_time = burning_cells / total_cells
            break

    return time_fire_reaches_town, coverage_at_time

if __name__ == "__main__":
    t, c = get_results(num_iterations=300)
    print(f"Time: {t}")
    print(f"Coverage: {c}")
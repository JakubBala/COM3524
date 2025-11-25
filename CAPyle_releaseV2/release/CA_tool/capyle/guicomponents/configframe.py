import tkinter as tk
import numpy as np
import os
import subprocess
import platform
from CA_tool.capyle.utils import gens_to_dims
from .gui_utils import (alerterror, alertcontinue)
from CA_tool.capyle.guicomponents import (_GenerationsUI, _GridDimensionsUI,
                                  _Separator, _NeighbourhoodUI, _RuleNumberUI,
                                  _StateColorsUI, _InitialGridUI)


class _ConfigFrame(tk.Frame):

    def __init__(self, parent, ca_config):
        tk.Frame.__init__(self, parent, padx=10)
        self.ca_config = ca_config
        self.ca_graph = None

        btn_reset = tk.Button(self, text="Reset configuration",
                              command=self.reset)
        btn_reset.pack()

        self.separator()

        # if self.ca_config.dimensions == 2:
        #     self.griddims_entry = _GridDimensionsUI(self)
        #     self.griddims_entry.pack(fill=tk.BOTH)
        # else:
        #     self.rulenum_entry = _RuleNumberUI(self)
        #     self.rulenum_entry.pack(fill=tk.BOTH)

        # self.separator()

        # Gererations
        self.generations_entry = _GenerationsUI(self)
        self.generations_entry.pack(fill=tk.BOTH)

        self.separator()

        # Neighbourhood selector gui
        self.nhood_select = _NeighbourhoodUI(self, self.ca_config.dimensions)
        self.nhood_select.pack(fill=tk.BOTH)

        self.separator()

        # Toggles for ignition sources (Power Plant / Incinerator)
        # Use Checkbuttons so user can select one, both, or none.
        # Keep state in BooleanVars and persist to ca_config in get_config().
        self.powerplant_var = tk.BooleanVar(value=getattr(self.ca_config, "power_plant_enabled", False))
        self.incinerator_var = tk.BooleanVar(value=getattr(self.ca_config, "incinerator_enabled", False))

        src_frame = tk.Frame(self)
        lbl = tk.Label(src_frame, text="Ignition sources:")
        lbl.pack(anchor=tk.W, padx=0, pady=(0, 4))

        cb_frame = tk.Frame(src_frame)
        cb_pp = tk.Checkbutton(src_frame, text="Power Plant", variable=self.powerplant_var,
                               command=self._on_sources_changed)
        cb_pp.pack(side=tk.LEFT, padx=4)

        cb_inc = tk.Checkbutton(src_frame, text="Incinerator", variable=self.incinerator_var,
                                command=self._on_sources_changed)
        cb_inc.pack(side=tk.LEFT, padx=4)

        cb_frame.pack(anchor=tk.W)
        src_frame.pack(fill=tk.BOTH, pady=(6,0))

        #self.separator()

        cb_frame.pack(anchor=tk.W)
        src_frame.pack(fill=tk.BOTH, pady=(6, 0))

        #self.separator()

        # Label to display when fire reaches town
        self.town_ignition_label = tk.Label(self, text="Town ignited after step: —", 
                                             fg="red", font=("Arial", 10, "bold"))
        self.town_ignition_label.pack(anchor=tk.W, padx=0, pady=(4, 0))
        
        # initial grid config options
        # self.init_grid = _InitialGridUI(self, self.ca_config)
        # self.init_grid.pack(fill=tk.BOTH)

        # self.separator()

        # Colour selector
        # self.state_colors = _StateColorsUI(self, self.ca_config, self.ca_graph)
        # self.state_colors.pack(fill=tk.BOTH)

        # btn_open_json = tk.Button(self, text="Open waterdrops.json",
        #                   command=self.open_waterdrops)
        # btn_open_json.pack()

        # refresh the frame and graph
        self.update(self.ca_config, self.ca_graph)

    def separator(self):
        """Generate a separator"""
        return _Separator(self).pack(fill=tk.BOTH, padx=5, pady=10)
    
    def _on_sources_changed(self):
        # immediate persist to config so other parts of the UI/code can read it
        self.ca_config.power_plant_enabled = bool(self.powerplant_var.get())
        self.ca_config.incinerator_enabled = bool(self.incinerator_var.get())

    def reset(self):
        """Reset all options to software defaults"""
        # if self.ca_config.dimensions == 2:
        #     self.griddims_entry.set_default()
        # else:
        #     self.rulenum_entry.set_default()
        self.generations_entry.set_default()
        self.nhood_select.set_default()

    def get_config(self, ca_config, validate=False):
        """Get the config from the UI and store in a CAConfig object"""
        ca_config.num_generations = self.generations_entry.get_value()
        ca_config.power_plant_enabled = bool(self.powerplant_var.get())
        ca_config.incinerator_enabled = bool(self.incinerator_var.get())

        if ca_config.dimensions == 2:
            # ca_config.grid_dims = self.griddims_entry.get_value()
            ca_config.nhood_arr = self.nhood_select.get_value() + 0
        else:
            ca_config.rule_num = self.rulenum_entry.get_value()
            ca_config.nhood_arr = self.nhood_select.get_value()[0] + 0
            centercell = (self.init_grid.selected.get() == 2)
            if centercell:
                ca_config.grid_dims = gens_to_dims(ca_config.num_generations)
                ca_config.initial_grid = np.zeros(ca_config.grid_dims)
                ig = self.__center_cell_set(ca_config.grid_dims,
                                            ca_config.states[-1])
                ca_config.set_initial_grid(ig)

        if not validate:
            return ca_config
        else:
            return self.__validate_and_warn(ca_config)

    def __center_cell_set(self, dims, state):
        new_row = np.zeros((1, dims[1]))
        center = dims[1]//2
        new_row[0, center] = state
        return new_row

    def __validate_and_warn(self, ca_config):
        """Validate the CAConfig object against criteria"""
        errcheck = self.__error_cases(ca_config)
        if errcheck is not None:
            alerterror(*errcheck)
            return ca_config, False

        # If complex task ask if user wishes to proceed
        proceedcheck = self.__ask_proceed_cases(ca_config)
        return ca_config, proceedcheck

    def __error_cases(self, ca_config):
        if ca_config.dimensions == 1:
            if ca_config.rule_num < 0 or ca_config.rule_num > 255:
                s = "Only 0-255 valid, {val} supplied"
                return "Rule number", s.format(val=ca_config.rule_num)

        if ca_config.dimensions == 2:
            if ca_config.grid_dims[0] < 3 or ca_config.grid_dims[1] < 3:
                s = "One or both of the grid dimensions is too small {d}"
                return ("Grid dimensions", s.format(d=ca_config.grid_dims))

        if ca_config.num_generations < 1:
            s = "Invalid generations {val} supplied"
            return "Generations", s.format(val=ca_config.num_generations)
        return None

    def __ask_proceed_cases(self, ca_config):
        complexity_val = (ca_config.num_generations * ca_config.grid_dims[0] *
                          ca_config.grid_dims[1])
        if complexity_val > 30000000:
            s = ("The combination of grid dims {d} and {x} generations may" +
                 " take a long time to run. Do you wish to continue?")
            s = s.format(d=ca_config.grid_dims, x=ca_config.num_generations)
            complexitycheck = alertcontinue("Complexity warning!", s)
            return complexitycheck
        return True

    def update(self, ca_config, ca_graph):
        self.ca_config = ca_config
        self.ca_graph = ca_graph
        # if ca_config.dimensions == 2:
        #     self.griddims_entry.set(self.griddims_entry.COLS,
        #                             self.ca_config.grid_dims[0])
        #     self.griddims_entry.set(self.griddims_entry.ROWS,
        #                             self.ca_config.grid_dims[1])
        # else:
        #     self.rulenum_entry.set(ca_config.rule_num)
        self.nhood_select.set(self.ca_config.nhood_arr)
        self.generations_entry.set(self.ca_config.num_generations)
        # sync ignition source checkboxes
        self.powerplant_var.set(bool(getattr(self.ca_config, "power_plant_enabled", False)))
        self.incinerator_var.set(bool(getattr(self.ca_config, "incinerator_enabled", False)))
        # self.init_grid.update_config(self.ca_config)
        # self.state_colors.update(self.ca_config, ca_graph)

        # Update town ignition label
        town_step = getattr(self.ca_config, "town_ignition_step", None)
        if town_step is not None:
            self.town_ignition_label.config(text=f"Town ignited at step: {town_step}")
        else:
            self.town_ignition_label.config(text="Town ignited at step: —")

    def open_waterdrops(self):
        """Open the JSON file one directory up."""
        # Path to file: one directory up from the current file
        json_path = os.path.join(os.path.dirname(__file__), "..", "waterdrops.json")
        json_path = os.path.abspath(json_path)

        if not os.path.exists(json_path):
            alerterror("File error", f"Could not find file:\n{json_path}")
            return

        # Try to open using OS default application
        system = platform.system()

        if system == "Windows":
            os.startfile(json_path)
        elif system == "Darwin":  # macOS
            subprocess.call(["open", json_path])
        else:  # Linux / other
            subprocess.call(["xdg-open", json_path])

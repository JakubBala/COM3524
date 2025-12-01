# COM 3524 – Team 13

This folder contains the code, based on CAPyle, that we have modified to simulate a wildfire based on the assignment brief.

## Prerequisites
Before starting, ensure Docker Desktop and X11 Server are installed. If they aren't, follow the instructions found [here](https://github.com/ac1asana/COM3524).

## Use
The tool runs much like before. Make sure docker and the X11 server (if necessary) are running, then depending on your system, run:

#### Linux
```bash
./linux.sh
```
#### Windows
```bash
.\windows_updated.bat
```

#### Mac
```bash
./mac.sh
```

The tool should run automatically, then select the Team 13 CAPyle tool from available options by entering "1".

Note that unfortunately we have only been able to verify this works on Windows as we do not have access to a linux or mac pc. Changes have been reflected in the linux and mac helper scripts anyway (untested).

## Features


### Changing the Water Dropping Plan

By default, the simulation runs without a water droping plan. Unfortunately we did not have time to add water plans as a toggle in the GUI, so to run a water dropping plan users will have to apply the following simple changes to the code:

Select water dropping plan for the power plant or incinerator by updating `CAPyle_releaseV2/release/ca_descriptions/real_valued_fire.pyreal_valued_fire.py` line 25.  
Line 25 for the powerplant water plan:
```python
    "waterdrops_powplant.json"
```

line 25 for the incinerator water plan:
```python
    "waterdrops_incinerator.json"
```

by default, the chosen water plan (see above) is not dropped. Update CAPyle_releaseV2/release/ca_descriptions/real_valued_fire.py line 429 to pass the chosen water dropping plan as a parameter:

line 429 to not drop any water (default): 
```python
    main()
```

line 429 to drop chosen water plan (do not edit): 
```python
    main(water_plan_path=water_json_path)
```

Close the GUI and re-run by selecting option 1 from the terminal again to apply these changes.

### Using the GUI

Inside the tool's GUI, toggles are available for:

#### Ignition Sources:
[] Power Plant  
[] Incinerator  
#### Long Term Interventions:
[] Extended Forest (West)  
[] Extended Forest (South)  
[] Flooded Canyon  
#### Run Regrowth Simulation:
[] Run Regrowth

Any combination of the toggles can be selected. That is, multiple, one, or no sources can be chosen. Multiple, one, or no interventions can be applied.

Running the regrowth simulation will not override the chosen interventions, but will override the ignition source toggles, as no ignition should happen in the regrowth simulation.

There is also a label for number of generations. Your chosen number of generations can be manually inputted.

### Once you have configured your options, click the 'Apply Configuration & Run CA' button at the bottom of the window to apply changes.

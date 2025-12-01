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

Depending on whether you are running from the power plant or incinerator, you can change the path on line 25 on `real_valued_fire.py`. For the powerplant:
```python
    "waterdrops_powplant.json"
```

For the incinerator:
```python
    "waterdrops_incinerator.json"
```

Alternatively, run without a water dropping plan by removing `water_plan_path` on line 429:
```python
    main()
```

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
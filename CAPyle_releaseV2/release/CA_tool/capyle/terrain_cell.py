
from enum import Enum
import numbers
import random

class TerrainType(Enum):
    CHAPARRAL = 1
    DENSE_FOREST = 2
    CANYON_SCRUBLAND = 3
    LAKE = 4
    SOURCE = 5
    TOWN = 6

IGNITION_PROB_TABLE = {
    TerrainType.CHAPARRAL: {
        TerrainType.CHAPARRAL: 0.45,
        TerrainType.CANYON_SCRUBLAND: 0.5,
        TerrainType.DENSE_FOREST: 0.25,
        TerrainType.TOWN: 0.25,
        TerrainType.LAKE: 0.0,
        TerrainType.SOURCE: 0.35
    },
    TerrainType.CANYON_SCRUBLAND: {
        TerrainType.CHAPARRAL: 0.45,
        TerrainType.CANYON_SCRUBLAND: 0.5,
        TerrainType.DENSE_FOREST: 0.25,
        TerrainType.TOWN: 0.35,
        TerrainType.LAKE: 0.0,
        TerrainType.SOURCE: 0.35
    },
    TerrainType.DENSE_FOREST: {
        TerrainType.CHAPARRAL: 0.15,
        TerrainType.CANYON_SCRUBLAND: 0.24,
        TerrainType.DENSE_FOREST: 0.15,
        TerrainType.TOWN: 0.20,
        TerrainType.LAKE: 0.0,
        TerrainType.SOURCE: 0.35
    },
    TerrainType.SOURCE: {
        TerrainType.CHAPARRAL: 0.8,
        TerrainType.CANYON_SCRUBLAND: 0.9,
        TerrainType.DENSE_FOREST: 0.7,
        TerrainType.TOWN: 0.95,
        TerrainType.LAKE: 0.0,
        TerrainType.SOURCE: 1.0
    },
    TerrainType.TOWN: {
        TerrainType.CHAPARRAL: 0.2,
        TerrainType.CANYON_SCRUBLAND: 0.2,
        TerrainType.DENSE_FOREST: 0.2,
        TerrainType.TOWN: 0.15,
        TerrainType.LAKE: 0.0,
        TerrainType.SOURCE: 0.35
    },
    TerrainType.LAKE: {
        TerrainType.CHAPARRAL: 0.0,
        TerrainType.CANYON_SCRUBLAND: 0.0,
        TerrainType.DENSE_FOREST: 0.0,
        TerrainType.TOWN: 0.0,
        TerrainType.LAKE: 0.0,
        TerrainType.SOURCE: 0.0
    },
}

class TerrainCell():
    def __init__(
        self, 
        type: TerrainType, 
        moisture_decay: float = 0.05,
        burn_threshold: float = 0.5,
        regen_rate: float = None,
        burn_rate: float = None,
        burning: bool = False,
        burnt: bool = False,
        waterdropped: bool = False,
        burnt_period: int = 500 # of steps a cell remains burnt out
    ):
        self.type = type
        self.moisture_decay_rate = moisture_decay
        self.burn_threshold = burn_threshold

        self.fuel = 1.0
        self.moisture = 0.0

        self.burning = burning
        self.regen_rate = regen_rate
        self.burn_rate = burn_rate
        self.waterdropped = waterdropped

        #burnt state tracking
        self.burnt = burnt
        self.burnt_timer = 0
        self.burnt_period = burnt_period
        self.burn_duration = 0

    def get_ignition_prob(self, ignition_source: TerrainType) -> float:
        return IGNITION_PROB_TABLE[ignition_source][self.type]

    def regenerate(self):
        # If cell is in burnt state, age the burnt timer and only recover after period
        if self.burnt:
            self.burnt_timer += 1
            if self.burnt_timer >= self.burnt_period:
                # burnt period complete -> allow slow recovery
                self.burnt = False
                self.burnt_timer = 0
                # give small residual fuel so regeneration can continue
                self.fuel = min(0.1, self.fuel + 0.1)
            return

        if self.type != TerrainType.TOWN and \
            self.type != TerrainType.LAKE and \
            self.type != TerrainType.SOURCE:
            if not self.burning:
                self.fuel = min(1.0, self.fuel + (self.regen_rate if self.regen_rate is not None else 0))
            self._strip_moisture()

    def ignite(self):
        if self.burnt:
            return
        
        match (self.type):
            case TerrainType.TOWN:
                self.burning = True
                self.burn_duration = 0
            case TerrainType.LAKE:
                return
            case TerrainType.SOURCE:
                self.burning = True
                self.burn_duration = 0
            case _:
                if self.moisture < self.burn_threshold:
                    if self.fuel >= self.burn_rate:
                        self.burning = True
                        self.fuel -= self.burn_rate
                        self.burn_duration = 0
                    else:
                        self.fuel = 0.0
        
                self._strip_moisture()

    def burn(self):
        if self.type == TerrainType.TOWN:
            return
        elif self.type == TerrainType.SOURCE:
            if random.random() > 0.2:
                return
            else:
                self.burning = False
        else:
            if self.fuel >= self.burn_rate:
                self.fuel -= self.burn_rate
                self.burn_duration += 1
            else:
                # burning finished, enter burnt state
                self.burning = False
                self.fuel = 0.0
                self.burnt = True
                self.burnt_timer = 0
                self.burn_duration = 0

            self._strip_moisture()
    
    def drop_water(self, max_moisture: float = 0.5):
        self.waterdropped = True
        if self.burnt:
            return # water drop has no effect on burnt cells
        match (self.type):
            case TerrainType.TOWN:
                return
            case TerrainType.LAKE:
                return
            case TerrainType.SOURCE:
                self.burning = True
            case _:
                if self.burning:
                    self.burning = False
                    self.moisture = min(self.moisture + 0.5 * max_moisture)
                else:
                    self.moisture = max_moisture
            
    def _strip_moisture(self):
        multiplier = 0.5 if not self.burning else 1
        self.moisture = max(0, self.moisture - multiplier * self.moisture_decay_rate)

def cell_to_state_index(cell: TerrainCell) -> int:
    if cell is None or isinstance(cell, numbers.Integral):
        return -1 

    base = (cell.type.value - 1) * 4

    if cell.waterdropped:
        return base + 2
    elif cell.burning:
        return base + 1
    elif cell.burnt:
        return base + 3
    else:
        return base + 0
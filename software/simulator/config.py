# software/simulator/config.py

# Runway info
RUNWAY_LENGTH_M = 2427  # meters
NUM_ZONES = 10

# Aircraft types and their impact factors
AIRCRAFT_TYPES = {
    "ATR72": {"weight_factor": 0.8, "rubber_factor": 0.5},
    "A320": {"weight_factor": 1.2, "rubber_factor": 0.8},
    "B738": {"weight_factor": 1.5, "rubber_factor": 1.0},
    "A321": {"weight_factor": 1.3, "rubber_factor": 0.9},
    "AT76": {"weight_factor": 1.0, "rubber_factor": 0.6},
}

# Weather ranges
WEATHER = {
    "temperature_C": (22, 38),
    "humidity_pct": (40, 80),
    "rain_mm": (0, 20),
}

# Maintenance thresholds
THRESHOLDS = {
    "stress": 100,
    "rubber_mm": 2,
    "cracks_mm": 5,
    "water_mm": 10,
    "fod_weight_g": 50,
}

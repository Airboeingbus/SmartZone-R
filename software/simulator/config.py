# software/simulator/config.py

# Runway info
RUNWAY_LENGTH_M = 2427  # meters
RUNWAY_WIDTH_M = 45     # meters
NUM_ZONES = 10

# Aircraft types with load factors and rubber impact
AIRCRAFT_TYPES = {
    "ATR72": {"weight_factor": 0.8, "rubber_factor": 0.5, "max_takeoff_kg": 22500},
    "A320": {"weight_factor": 1.2, "rubber_factor": 0.8, "max_takeoff_kg": 78000},
    "B738": {"weight_factor": 1.5, "rubber_factor": 1.0, "max_takeoff_kg": 79000},
    "A321": {"weight_factor": 1.3, "rubber_factor": 0.9, "max_takeoff_kg": 93000},
    "AT76": {"weight_factor": 1.0, "rubber_factor": 0.6, "max_takeoff_kg": 12800},
}

# Seasonal weather ranges (example for Kuala Lumpur)
WEATHER = {
    "temperature_C": {
        "avg": (27, 35), 
        "monsoon": (25, 33)
    },
    "humidity_pct": {
        "avg": (50, 75),
        "monsoon": (70, 90)
    },
    "rain_mm": {
        "avg": (0, 10),
        "monsoon": (10, 25)
    },
    "wind_speed_mps": (0, 10),  # optional for future use
    "wind_direction_deg": (0, 360),
}

# Maintenance thresholds
THRESHOLDS = {
    "stress": 100,
    "rubber_mm": 2,
    "cracks_mm": 5,
    "water_mm": 10,
    "fod_weight_g": 50,
}

# Takeoff/landing stress multipliers
TAKEOFF_STRESS_FACTOR = 1.2
LANDING_STRESS_FACTOR = 1.0
import random
from config import AIRCRAFT_TYPES, NUM_ZONES

def generate_flight_id():
    return f"FL{random.randint(1000,9999)}"

def pick_aircraft():
    return random.choice(list(AIRCRAFT_TYPES.keys()))

def assign_zone():
    return random.randint(1, NUM_ZONES)

def pick_operation():
    """Randomly decide if the flight is takeoff or landing"""
    return random.choice(["takeoff", "landing"])
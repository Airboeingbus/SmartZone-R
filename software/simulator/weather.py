# software/simulator/weather.py
import random
from config import WEATHER

def generate_weather():
    """Generate random weather conditions"""
    return {
        "temperature_C": round(random.uniform(*WEATHER["temperature_C"]), 2),
        "humidity_pct": round(random.uniform(*WEATHER["humidity_pct"]), 2),
        "rain_mm": round(random.uniform(*WEATHER["rain_mm"]), 2),
    }

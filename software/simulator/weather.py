import random
from config import WEATHER

def generate_weather(month=1):
    """Generate random weather conditions based on month (1-12)"""
    # Monsoon months: May to October
    season = "monsoon" if month in range(5, 11) else "avg"
    
    return {
        "temperature_C": round(random.uniform(*WEATHER["temperature_C"][season]), 2),
        "humidity_pct": round(random.uniform(*WEATHER["humidity_pct"][season]), 2),
        "rain_mm": round(random.uniform(*WEATHER["rain_mm"][season]), 2),
        "wind_speed_mps": round(random.uniform(*WEATHER["wind_speed_mps"]), 2),
        "wind_direction_deg": round(random.uniform(*WEATHER["wind_direction_deg"]), 2)
    }
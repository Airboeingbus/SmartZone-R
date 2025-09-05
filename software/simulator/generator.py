# software/simulator/generator.py
import random
from datetime import datetime, timedelta
import csv
from config import AIRCRAFT_TYPES, THRESHOLDS, NUM_ZONES
from flights import generate_flight_id, pick_aircraft, assign_zone
from weather import generate_weather

# Initialize runway metrics per zone
runway_metrics = {
    zone: {
        "stress": 0.0,
        "rubber_mm": random.uniform(5, 10),
        "cracks_mm": random.uniform(0, 2),
        "water_mm": 0.0,
        "fod_weight_g": 0.0,
    } for zone in range(1, NUM_ZONES + 1)
}

def simulate_flight(timestamp):
    flight_id = generate_flight_id()
    aircraft = pick_aircraft()
    zone = assign_zone()
    weather = generate_weather()

    aircraft_factor = AIRCRAFT_TYPES[aircraft]["weight_factor"]
    rubber_factor = AIRCRAFT_TYPES[aircraft]["rubber_factor"]

    stress = round(random.uniform(0.5, 2.0) * aircraft_factor, 2)
    rubber_wear = round(random.uniform(0.1, 0.5) * rubber_factor, 2)
    cracks_growth = round(random.uniform(0.05, 0.2), 2)
    water_accum = round(weather["rain_mm"] * random.uniform(0.1, 0.5), 2)
    fod_weight = round(random.uniform(0, 5), 2)

    metrics = runway_metrics[zone]
    metrics["stress"] += stress * (1 + weather["humidity_pct"] / 100)
    metrics["rubber_mm"] = max(metrics["rubber_mm"] - rubber_wear, 0)
    metrics["cracks_mm"] += cracks_growth
    metrics["water_mm"] = water_accum
    metrics["fod_weight_g"] = fod_weight

    anomaly = (
        metrics["stress"] > THRESHOLDS["stress"]
        or metrics["rubber_mm"] < THRESHOLDS["rubber_mm"]
        or metrics["cracks_mm"] > THRESHOLDS["cracks_mm"]
        or metrics["water_mm"] > THRESHOLDS["water_mm"]
        or metrics["fod_weight_g"] > THRESHOLDS["fod_weight_g"]
    )

    return [
        timestamp.isoformat(),
        flight_id,
        aircraft,
        zone,
        round(metrics["rubber_mm"], 2),
        round(metrics["cracks_mm"], 2),
        round(metrics["water_mm"], 2),
        round(metrics["stress"], 2),
        round(metrics["fod_weight_g"], 2),
        round(weather["temperature_C"], 2),
        round(weather["humidity_pct"], 2),
        round(weather["rain_mm"], 2),
        int(anomaly),
    ]

def simulate_day(start_time=datetime(2025, 9, 5, 0, 0), interval_minutes=30):
    flights = []
    current_time = start_time
    end_time = start_time + timedelta(hours=24)

    while current_time < end_time:
        flights.append(simulate_flight(current_time))
        current_time += timedelta(minutes=interval_minutes + random.randint(-5,5))

    return flights

if __name__ == "__main__":
    flights_data = simulate_day()
    header = [
        "timestamp","flight_id","aircraft","zone",
        "rubber_mm","cracks_mm","water_mm","stress","fod_weight_g",
        "temperature_C","humidity_pct","rain_mm","anomaly"
    ]
    output_file = "../data/runway_data.csv"
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(flights_data)
    print(f"Runway data written to {output_file}")

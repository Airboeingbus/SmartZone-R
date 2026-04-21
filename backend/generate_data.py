"""
Data Generator for SmartZone-R
Generates realistic runway monitoring data for Chennai airport (MAA)
Indian airports, aircraft types, and airlines
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Configuration
AIRPORT_CODE = "MAA"  # Chennai airport
DB_PATH = os.path.join(os.path.dirname(__file__), "smartzone_r.db")
NUM_FLIGHTS = 150  # Realistic daily flight count
NUM_ZONES = 10

# Indian Airlines
AIRLINES = [
    "AI", "6E", "SG", "G8", "UK", "AL", "AZ", "BI"  # Air India, IndiGo, SpiceJet, GoAir, Vistara, Alliance, AirAsia, Kingfisher
]

# Aircraft operating in India
AIRCRAFT = [
    "B787", "A320", "B777", "A321", "B737", "Q400", "ATR42", "ATR72", 
    "A380", "B789", "A330", "E190", "B738"
]

# Generate realistic flight IDs
def generate_flight_id():
    airline = np.random.choice(AIRLINES)
    number = np.random.randint(1, 9999)
    return f"{airline}{number:04d}"

# Create database schema
def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing table if present
    cursor.execute("DROP TABLE IF EXISTS runway_data")
    
    # Create table with proper schema
    cursor.execute("""
        CREATE TABLE runway_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            flight_id TEXT NOT NULL,
            aircraft TEXT NOT NULL,
            zone INTEGER NOT NULL,
            rubber_mm REAL NOT NULL,
            cracks_mm REAL NOT NULL,
            water_mm REAL NOT NULL,
            stress REAL NOT NULL,
            fod_weight_g REAL NOT NULL,
            temperature_C REAL NOT NULL,
            humidity_pct REAL NOT NULL,
            rain_mm REAL NOT NULL,
            anomaly INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database created: {DB_PATH}")

# Generate realistic runway data
def generate_flight_data():
    """Generate realistic runway monitoring data for flights"""
    data = []
    
    # Start from 24 hours ago
    base_time = datetime.now() - timedelta(hours=24)
    
    for _ in range(NUM_FLIGHTS):
        # Random timestamp within last 24 hours
        flight_time = base_time + timedelta(
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60),
            seconds=np.random.randint(0, 60)
        )
        
        flight_id = generate_flight_id()
        aircraft = np.random.choice(AIRCRAFT)
        zone = np.random.randint(1, NUM_ZONES + 1)
        
        # Realistic physics: heavier aircraft = higher stress
        aircraft_weight_factor = {
            "B787": 3.5, "A380": 4.0, "B777": 3.8, "A330": 3.6,
            "A321": 2.5, "B738": 2.2, "A320": 2.0, "B737": 2.1,
            "Q400": 1.5, "ATR72": 1.2, "ATR42": 1.0,
            "A350": 3.7, "E190": 1.8, "B789": 3.6
        }.get(aircraft, 2.5)
        
        # Stress increases with zone position (higher at landing zone)
        zone_factor = 0.5 + (zone / NUM_ZONES) * 1.5
        
        # Base stress with realistic variation
        base_stress = 50 * aircraft_weight_factor * zone_factor
        stress = base_stress + np.random.normal(0, 10)
        stress = max(0, min(100, stress))  # Clamp 0-100
        
        # Rubber depth decreases with use
        rubber_base = 12 - (zone / NUM_ZONES) * 8
        rubber_mm = rubber_base + np.random.normal(0, 1)
        rubber_mm = max(0.5, min(20, rubber_mm))
        
        # Cracks increase with stress
        cracks_mm = (stress / 100) * 15 + np.random.normal(0, 2)
        cracks_mm = max(0, min(50, cracks_mm))
        
        # Water presence (monsoon effect in India)
        water_mm = np.random.exponential(scale=2) if np.random.random() < 0.3 else 0
        water_mm = max(0, min(200, water_mm))
        
        # FOD (Foreign Object Debris) - random but correlated with zone
        fod_weight_g = np.random.exponential(scale=50) if np.random.random() < 0.4 else 0
        fod_weight_g = max(0, min(5000, fod_weight_g))
        
        # Weather
        temperature_C = 25 + np.random.normal(0, 5)
        humidity_pct = 70 + np.random.normal(0, 15)
        humidity_pct = max(0, min(100, humidity_pct))
        
        rain_mm = water_mm * 0.3  # Correlation
        
        # Anomaly detection: stress > 75 or rubber < 2 or cracks > 20
        anomaly = 1 if (stress > 75 or rubber_mm < 2 or cracks_mm > 20 or fod_weight_g > 1000) else 0
        
        data.append({
            'timestamp': flight_time.isoformat(),
            'flight_id': flight_id,
            'aircraft': aircraft,
            'zone': zone,
            'rubber_mm': round(rubber_mm, 2),
            'cracks_mm': round(cracks_mm, 2),
            'water_mm': round(water_mm, 2),
            'stress': round(stress, 2),
            'fod_weight_g': round(fod_weight_g, 2),
            'temperature_C': round(temperature_C, 1),
            'humidity_pct': round(humidity_pct, 1),
            'rain_mm': round(rain_mm, 2),
            'anomaly': anomaly
        })
    
    return pd.DataFrame(data)

# Insert data into database
def insert_data_to_db(df):
    """Insert dataframe into SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('runway_data', conn, if_exists='append', index=False)
    conn.commit()
    
    # Get stats
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM runway_data")
    count = cursor.fetchone()[0]
    
    cursor.execute("SELECT zone, COUNT(*) as flights FROM runway_data GROUP BY zone")
    zone_stats = cursor.fetchall()
    
    conn.close()
    
    logger.info(f"Inserted {count} flight records into database")
    logger.info(f"Flight distribution by zone:")
    for zone, flights in zone_stats:
        logger.info(f"  Zone {zone}: {flights} flights")

# Main execution
def main():
    logger.info("=" * 60)
    logger.info("SmartZone-R Data Generator")
    logger.info("Chennai Airport (MAA) Runway Monitoring")
    logger.info("=" * 60)
    
    logger.info(f"Configuration:")
    logger.info(f"  Airport: {AIRPORT_CODE} (Chennai - Meenambakkam)")
    logger.info(f"  Flights to generate: {NUM_FLIGHTS}")
    logger.info(f"  Zones: {NUM_ZONES}")
    logger.info(f"  Database: {DB_PATH}")
    
    logger.info(f"Generating data...")
    create_database()
    
    logger.info(f"Creating {NUM_FLIGHTS} flight records...")
    df = generate_flight_data()
    
    logger.info(f"Inserting into database...")
    insert_data_to_db(df)
    
    logger.info("=" * 60)
    logger.info("Data generation complete!")
    logger.info("=" * 60)
    logger.info("Sample data (first 5 records):")
    logger.info(df.head().to_string())
    
    logger.info("Start the server with:")
    logger.info("  cd SmartZone-R/backend")
    logger.info("  python -m uvicorn main:app --reload")
    logger.info("Visit: http://localhost:8000")

if __name__ == "__main__":
    main()

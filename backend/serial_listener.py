"""
Serial Listener for SmartZone-R ESP32
Reads JSON sensor data from ESP32 over Serial and inserts into SQLite database.
Runs as a background daemon thread.
"""

import serial
import json
import sqlite3
import os
import time
import threading
import logging
from datetime import datetime
from dotenv import load_dotenv
import random
import string

# Setup logging
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
SERIAL_BAUDRATE = int(os.getenv("SERIAL_BAUDRATE", "115200"))
DB_PATH = os.getenv("DB_PATH", "smartzone_r.db")
RECONNECT_INTERVAL = 10  # seconds

# Ensure absolute DB path
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)


class SerialListener:
    """Manages serial connection and data ingestion from ESP32"""

    def __init__(self):
        self.serial_conn = None
        self.running = False
        self.connected = False
        self.last_reading = None
        self.total_inserted = 0
        self.lock = threading.Lock()

    def connect(self):
        """Attempt to connect to serial port"""
        try:
            self.serial_conn = serial.Serial(
                port=SERIAL_PORT,
                baudrate=SERIAL_BAUDRATE,
                timeout=1,
                write_timeout=1,
            )
            self.connected = True
            logger.info(f"Serial connected: {SERIAL_PORT} @ {SERIAL_BAUDRATE} baud")
            return True
        except (serial.SerialException, FileNotFoundError) as e:
            logger.error(f"Serial error: {e}")
            self.connected = False
            return False

    def parse_json(self, line: str) -> dict:
        """Parse and validate JSON from ESP32"""
        try:
            data = json.loads(line)
            # Validate required fields
            required = ["zone", "temp", "humidity", "stress", "water_mm", "fod", "timestamp"]
            if not all(k in data for k in required):
                logger.warning(f"Incomplete JSON (missing fields): {line[:80]}")
                return None
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON: {line[:80]} - {e}")
            return None

    def map_to_schema(self, esp_data: dict) -> dict:
        """Map ESP32 JSON fields to runway_data table schema"""
        # Generate missing fields
        flight_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        aircraft_types = ["B787", "A320", "B777", "A321", "B738", "Q400", "ATR72", "E190"]
        
        return {
            "timestamp": esp_data.get("timestamp", datetime.now().isoformat()),
            "flight_id": flight_id,
            "aircraft": random.choice(aircraft_types),
            "zone": int(esp_data["zone"]),
            "rubber_mm": float(esp_data.get("rubber_mm", random.uniform(3, 12))),  # Estimate
            "cracks_mm": float(esp_data.get("cracks_mm", random.uniform(5, 20))),   # Estimate
            "water_mm": float(esp_data["water_mm"]),
            "stress": float(esp_data["stress"]),
            "fod_weight_g": float(esp_data["fod"]),
            "temperature_C": float(esp_data["temp"]),
            "humidity_pct": float(esp_data["humidity"]),
            "rain_mm": float(esp_data.get("rain_mm", 0.0)),  # Default if not provided
            "anomaly": self.calculate_anomaly(esp_data),
        }

    def calculate_anomaly(self, esp_data: dict) -> int:
        """Determine if data point is anomalous"""
        stress = float(esp_data["stress"])
        water = float(esp_data["water_mm"])
        fod = float(esp_data["fod"])
        
        # Anomaly if stress too high, water present during flight, or high FOD
        if stress > 75 or water > 5 or fod > 500:
            return 1
        return 0

    def insert_into_db(self, data: dict) -> bool:
        """Insert validated data into SQLite database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO runway_data (
                    timestamp, flight_id, aircraft, zone,
                    rubber_mm, cracks_mm, water_mm, stress,
                    fod_weight_g, temperature_C, humidity_pct,
                    rain_mm, anomaly
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["timestamp"],
                data["flight_id"],
                data["aircraft"],
                data["zone"],
                data["rubber_mm"],
                data["cracks_mm"],
                data["water_mm"],
                data["stress"],
                data["fod_weight_g"],
                data["temperature_C"],
                data["humidity_pct"],
                data["rain_mm"],
                data["anomaly"],
            ))
            
            conn.commit()
            conn.close()
            
            with self.lock:
                self.total_inserted += 1
                self.last_reading = datetime.now().isoformat()
            
            logger.info(
                f"Inserted: Zone {data['zone']}, "
                f"Stress {data['stress']:.1f}%, "
                f"Temp {data['temperature_C']:.1f}C "
                f"[Total: {self.total_inserted}]"
            )
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return False

    def read_loop(self):
        """Main serial reading loop (runs in background thread)"""
        reconnect_timer = 0
        
        while self.running:
            # Attempt connection if not connected
            if not self.connected:
                if reconnect_timer <= 0:
                    logger.info(f"Attempting to connect to {SERIAL_PORT}...")
                    if self.connect():
                        reconnect_timer = 0
                    else:
                        reconnect_timer = RECONNECT_INTERVAL
                        time.sleep(1)
                        continue
                else:
                    reconnect_timer -= 1
                    time.sleep(1)
                    continue
            
            # Read from serial
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode("utf-8").strip()
                    
                    if line:
                        # Parse JSON
                        esp_data = self.parse_json(line)
                        if esp_data:
                            # Map to schema
                            db_data = self.map_to_schema(esp_data)
                            # Insert into database
                            self.insert_into_db(db_data)
                else:
                    time.sleep(0.1)
                    
            except (serial.SerialException, UnicodeDecodeError) as e:
                logger.error(f"Serial read error: {e}")
                self.connected = False
                reconnect_timer = RECONNECT_INTERVAL
                time.sleep(1)

    def start(self):
        """Start serial listener as background daemon thread"""
        if not os.path.exists(DB_PATH):
            logger.error(f"Database not found: {DB_PATH}")
            return False
        
        self.running = True
        thread = threading.Thread(target=self.read_loop, daemon=True)
        thread.start()
        logger.info("Serial Listener started as background daemon")
        return True

    def stop(self):
        """Stop the serial listener"""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        logger.info("Serial Listener stopped")

    def get_status(self) -> dict:
        """Get current listener status"""
        with self.lock:
            return {
                "connected": self.connected,
                "port": SERIAL_PORT,
                "last_reading": self.last_reading,
                "total_inserted": self.total_inserted,
            }


# Global listener instance
serial_listener = SerialListener()


def start_serial_listener():
    """Initialize and start the serial listener"""
    serial_listener.start()


def stop_serial_listener():
    """Stop the serial listener"""
    serial_listener.stop()


def get_listener_status() -> dict:
    """Get seriallistener status"""
    return serial_listener.get_status()

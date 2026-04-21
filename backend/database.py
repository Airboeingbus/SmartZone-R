"""
Database module for SmartZone-R.
Handles data loading from SQLite/CSV and data validation.
"""

import sqlite3
import pandas as pd
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger(__name__)

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "../software/data/smartzone_r.db")
CSV_PATH = os.getenv("CSV_PATH", "../software/data/runway_data.csv")

# Ensure absolute paths
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)
if not os.path.isabs(CSV_PATH):
    CSV_PATH = os.path.join(os.path.dirname(__file__), CSV_PATH)


def load_data() -> pd.DataFrame:
    """
    Load runway data from SQLite or CSV fallback.
    
    Returns:
        pd.DataFrame: Validated runway data
    """
    df = None
    
    # Try SQLite first
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql("SELECT * FROM runway_data", conn, parse_dates=["timestamp"])
            conn.close()
            return validate_data(df)
        except Exception as e:
            logger.warning(f"SQLite error: {e}, falling back to CSV...")
    
    # Fall back to CSV
    if os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
            return validate_data(df)
        except Exception as e:
            logger.error(f"CSV error: {e}")
            return pd.DataFrame()
    
    logger.warning("No data source found")
    return pd.DataFrame()


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean runway data.
    
    Args:
        df (pd.DataFrame): Raw data
    
    Returns:
        pd.DataFrame: Cleaned data
    """
    if df is None or df.empty:
        return df
    
    df = df.copy()
    
    # Valid ranges
    ranges = {
        "rubber_mm": (0, 20),
        "cracks_mm": (0, 50),
        "water_mm": (0, 200),
        "stress": (0, 1000),
        "fod_weight_g": (0, 5000),
        "temperature_C": (-10, 60),
        "humidity_pct": (0, 100),
        "rain_mm": (0, 500),
    }
    
    # Drop nulls
    df = df.dropna(subset=["timestamp"])
    
    # Clip numeric columns
    for col, (min_val, max_val) in ranges.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].clip(min_val, max_val)
    
    return df


def get_zone_summary(df: pd.DataFrame) -> list:
    """
    Get per-zone aggregated metrics.
    
    Args:
        df (pd.DataFrame): Flight data
    
    Returns:
        list: List of dicts with zone summary
    """
    if df.empty:
        return []
    
    summaries = []
    for zone in sorted(df["zone"].unique()):
        zone_data = df[df["zone"] == zone]
        
        status = "normal"
        avg_stress = zone_data["stress"].mean()
        if avg_stress > 85:
            status = "critical"
        elif avg_stress > 70:
            status = "high"
        
        summaries.append({
            "zone": int(zone),
            "avg_stress": round(float(avg_stress), 2),
            "max_stress": round(float(zone_data["stress"].max()), 2),
            "avg_rubber": round(float(zone_data["rubber_mm"].mean()), 2),
            "avg_cracks": round(float(zone_data["cracks_mm"].mean()), 2),
            "avg_water": round(float(zone_data["water_mm"].mean()), 2),
            "avg_fod": round(float(zone_data["fod_weight_g"].mean()), 2),
            "flight_count": int(len(zone_data)),
            "anomaly_count": int(zone_data["anomaly"].sum()),
            "status": status
        })
    
    return summaries


def get_recent_flights(df: pd.DataFrame, n: int = 50) -> list:
    """
    Get most recent flight records.
    
    Args:
        df (pd.DataFrame): Flight data
        n (int): Number of flights
    
    Returns:
        list: Recent flight dicts
    """
    if df.empty:
        return []
    
    df_sorted = df.sort_values("timestamp", ascending=False).head(n)
    
    flights = []
    for _, row in df_sorted.iterrows():
        flights.append({
            "timestamp": row["timestamp"].isoformat() if pd.notna(row["timestamp"]) else "",
            "flight_id": str(row["flight_id"]),
            "aircraft": str(row["aircraft"]),
            "zone": int(row["zone"]),
            "rubber_mm": round(float(row["rubber_mm"]), 2),
            "cracks_mm": round(float(row["cracks_mm"]), 2),
            "water_mm": round(float(row["water_mm"]), 2),
            "stress": round(float(row["stress"]), 2),
            "fod_weight_g": round(float(row["fod_weight_g"]), 2),
            "temperature_C": round(float(row["temperature_C"]), 1),
            "humidity_pct": round(float(row["humidity_pct"]), 1),
            "rain_mm": round(float(row["rain_mm"]), 2),
            "anomaly": int(row["anomaly"])
        })
    
    return flights


def get_flights_by_zone(df: pd.DataFrame, zone: int, n: int = 20) -> list:
    """
    Get recent flights for a specific zone.
    
    Args:
        df (pd.DataFrame): Flight data
        zone (int): Zone number
        n (int): Number of flights
    
    Returns:
        list: Flight dicts for that zone
    """
    if df.empty:
        return []
    
    df_zone = df[df["zone"] == zone].sort_values("timestamp", ascending=False).head(n)
    return get_recent_flights(df_zone, n)


def get_active_alerts(df: pd.DataFrame, thresholds: dict = None) -> list:
    """
    Get records that trigger alerts based on thresholds.
    
    Args:
        df (pd.DataFrame): Flight data
        thresholds (dict): Threshold values
    
    Returns:
        list: Alert records
    """
    if df.empty:
        return []
    
    if thresholds is None:
        thresholds = {
            "stress": 85,
            "rubber_mm": 5,
            "cracks_mm": 10,
            "water_mm": 3,
            "fod_weight_g": 50
        }
    
    alerts = []
    
    for _, row in df.iterrows():
        reasons = []
        severity = "normal"
        
        if row["stress"] > thresholds["stress"]:
            reasons.append(f"High stress ({row['stress']:.0f}%)")
            severity = "critical"
        
        if row["rubber_mm"] > thresholds["rubber_mm"]:
            reasons.append(f"Rubber buildup ({row['rubber_mm']:.1f}mm)")
            if severity != "critical":
                severity = "high"
        
        if row["cracks_mm"] > thresholds["cracks_mm"]:
            reasons.append(f"Surface cracks ({row['cracks_mm']:.1f}mm)")
            if severity == "normal":
                severity = "medium"
        
        if row["water_mm"] > thresholds["water_mm"]:
            reasons.append(f"Water accumulation ({row['water_mm']:.1f}mm)")
            if severity == "normal":
                severity = "medium"
        
        if row["fod_weight_g"] > thresholds["fod_weight_g"]:
            reasons.append(f"FOD detected ({row['fod_weight_g']:.0f}g)")
            if severity == "normal":
                severity = "high"
        
        if row["anomaly"] > 0:
            reasons.append("Anomaly detected")
            if severity == "normal":
                severity = "medium"
        
        if reasons:
            alerts.append({
                "timestamp": row["timestamp"].isoformat() if pd.notna(row["timestamp"]) else "",
                "flight_id": str(row["flight_id"]),
                "aircraft": str(row["aircraft"]),
                "zone": int(row["zone"]),
                "severity": severity,
                "reasons": reasons,
                "stress": round(float(row["stress"]), 2),
                "rubber_mm": round(float(row["rubber_mm"]), 2),
                "cracks_mm": round(float(row["cracks_mm"]), 2),
                "water_mm": round(float(row["water_mm"]), 2),  
                "fod_weight_g": round(float(row["fod_weight_g"]), 2)
            })
    
    return sorted(alerts, key=lambda x: {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "normal": 3
    }.get(x["severity"], 4), reverse=True)


def get_time_series(df: pd.DataFrame, metric: str, zone: int = None) -> dict:
    """
    Get time series data for a metric.
    
    Args:
        df (pd.DataFrame): Flight data
        metric (str): Metric name (stress, rubber_mm, etc.)
        zone (int): Filter by zone (optional)
    
    Returns:
        dict: Time series with labels and datasets
    """
    if df.empty or metric not in df.columns:
        return {"labels": [], "datasets": []}
    
    if zone is not None:
        df_filtered = df[df["zone"] == zone]
    else:
        df_filtered = df
    
    df_sorted = df_filtered.sort_values("timestamp")
    
    # For multiple zones, group by zone
    if zone is None and len(df_filtered["zone"].unique()) > 1:
        datasets = []
        colors = ["#00d4ff", "#00ff88", "#ffaa00", "#ff3333", "#0099ff"]
        
        for i, z in enumerate(sorted(df_filtered["zone"].unique())):
            z_data = df_sorted[df_sorted["zone"] == z]
            datasets.append({
                "label": f"Zone {int(z):02d}",
                "data": z_data[metric].tolist(),
                "borderColor": colors[i % len(colors)],
                "backgroundColor": f"{colors[i % len(colors)]}20",
                "tension": 0.3
            })
        
        return {
            "labels": [t.isoformat() for t in df_sorted["timestamp"].unique()],
            "datasets": datasets
        }
    else:
        return {
            "labels": [t.isoformat() for t in df_sorted["timestamp"]],
            "datasets": [{
                "label": metric.replace("_", " ").title(),
                "data": df_sorted[metric].tolist(),
                "borderColor": "#00d4ff",
                "backgroundColor": "#00d4ff40",
                "tension": 0.3
            }]
        }


def get_heatmap_data(df: pd.DataFrame) -> dict:
    """
    Get zone × metric heatmap data.
    
    Args:
        df (pd.DataFrame): Flight data
    
    Returns:
        dict: Heatmap matrix
    """
    if df.empty:
        return {"zones": [], "metrics": [], "data": []}
    
    zones = sorted(df["zone"].unique())
    metrics = ["stress", "rubber_mm", "cracks_mm", "water_mm", "fod_weight_g"]
    
    # Normalize metrics to 0-100 risk scale
    risk_map = {
        "stress": (0, 100),
        "rubber_mm": (0, 20),
        "cracks_mm": (0, 50),
        "water_mm": (0, 20),
        "fod_weight_g": (0, 500)
    }
    
    data = []
    for zone in zones:
        zone_data = df[df["zone"] == zone]
        row = []
        for metric in metrics:
            avg_val = zone_data[metric].mean()
            min_val, max_val = risk_map[metric]
            risk_pct = min(100, max(0, (avg_val / max_val) * 100))
            row.append(round(risk_pct, 1))
        data.append(row)
    
    return {
        "zones": [int(z) for z in zones],
        "metrics": ["Stress %", "Rubber mm", "Cracks mm", "Water mm", "FOD g"],
        "data": data
    }


# Database connection helpers for WebSocket and other async operations
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path=None):
    """Context manager for database connections."""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params=None, fetch_one=False, fetch_all=False, db_path=None):
    """Execute a database query and return results."""
    if db_path is None:
        db_path = DB_PATH
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None if fetch_one or fetch_all else 0

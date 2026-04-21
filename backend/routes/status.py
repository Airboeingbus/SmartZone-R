"""
Status endpoints for SmartZone-R API.
"""

import os
from datetime import datetime
from fastapi import APIRouter
from models import SystemStatus
from database import load_data, get_recent_flights, get_active_alerts

router = APIRouter(prefix="/api/status", tags=["status"])

START_TIME = datetime.now()


@router.get("", response_model=SystemStatus)
async def get_status():
    """Get system health and statistics."""
    df = load_data()
    
    db_path = os.getenv("DB_PATH", "../software/data/smartzone_r.db")
    csv_path = os.getenv("CSV_PATH", "../software/data/runway_data.csv")
    
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(__file__), "..", db_path)
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "..", csv_path)
    
    db_connected = os.path.exists(db_path)
    csv_connected = os.path.exists(csv_path)
    
    last_update = ""
    if not df.empty and "timestamp" in df.columns:
        last_update = df["timestamp"].max().isoformat()
    
    total_zones = int(df["zone"].max()) if not df.empty else 0
    total_flights = len(df)
    
    # Count active alerts
    alerts = get_active_alerts(df)
    active_alerts = len([a for a in alerts if a["severity"] in ["critical", "high"]])
    
    uptime = (datetime.now() - START_TIME).total_seconds()
    airport_code = os.getenv("AIRPORT_CODE", "MAA")
    
    return SystemStatus(
        db_connected=db_connected,
        csv_connected=csv_connected,
        last_update=last_update,
        total_zones=total_zones,
        total_flights=total_flights,
        active_alerts=active_alerts,
        uptime_seconds=uptime,
        airport_code=airport_code
    )

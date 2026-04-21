"""
Alert endpoints for SmartZone-R API.
"""

from typing import List
from fastapi import APIRouter
from models import AlertRecord, AlertSummary
from database import load_data, get_active_alerts

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Default thresholds
DEFAULT_THRESHOLDS = {
    "stress": 85,
    "rubber_mm": 5,
    "cracks_mm": 10,
    "water_mm": 3,
    "fod_weight_g": 50
}


@router.get("", response_model=List[AlertRecord])
async def get_alerts(severity: str = None):
    """Get alerts, optionally filtered by severity."""
    df = load_data()
    alerts = get_active_alerts(df, DEFAULT_THRESHOLDS)
    
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    
    return alerts


@router.get("/critical", response_model=List[AlertRecord])
async def get_critical_alerts():
    """Get only critical severity alerts."""
    df = load_data()
    alerts = get_active_alerts(df, DEFAULT_THRESHOLDS)
    return [a for a in alerts if a["severity"] == "critical"]


@router.get("/summary", response_model=AlertSummary)
async def get_alerts_summary():
    """Get count of alerts by severity."""
    df = load_data()
    alerts = get_active_alerts(df, DEFAULT_THRESHOLDS)
    
    critical_count = len([a for a in alerts if a["severity"] == "critical"])
    high_count = len([a for a in alerts if a["severity"] == "high"])
    medium_count = len([a for a in alerts if a["severity"] == "medium"])
    normal_count = len([a for a in alerts if a["severity"] == "normal"])
    
    return AlertSummary(
        critical=critical_count,
        high=high_count,
        medium=medium_count,
        normal=normal_count,
        total=len(alerts)
    )


@router.get("/zones", response_model=dict)
async def get_alerts_by_zone():
    """Get alert count per zone."""
    df = load_data()
    alerts = get_active_alerts(df, DEFAULT_THRESHOLDS)
    
    zone_counts = {}
    for zone in sorted(df["zone"].unique()):
        zone_alerts = [a for a in alerts if a["zone"] == zone]
        zone_counts[int(zone)] = len(zone_alerts)
    
    return zone_counts

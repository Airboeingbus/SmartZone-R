"""
Analytics endpoints for SmartZone-R API.
"""

from typing import List, Optional
from fastapi import APIRouter
from models import (
    AnalyticsSummary, ZoneSummary, TimeSeriesData, HeatmapData
)
from database import (
    load_data, get_zone_summary, get_time_series, get_heatmap_data,
    get_active_alerts
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary():
    """Get high-level analytics overview."""
    df = load_data()
    
    if df.empty:
        return AnalyticsSummary(
            total_flights=0,
            anomaly_rate=0.0,
            worst_zone=0,
            worst_zone_status="normal",
            avg_stress=0.0,
            avg_rubber=0.0,
            avg_temperature=0.0,
            avg_humidity=0.0,
            maintenance_urgent_zones=[],
            maintenance_inspect_zones=[]
        )
    
    total_flights = len(df)
    anomaly_rate = (df["anomaly"].sum() / total_flights * 100) if total_flights > 0 else 0
    
    zone_summaries = get_zone_summary(df)
    worst_zone = max(zone_summaries, key=lambda x: x["avg_stress"])
    
    avg_stress = df["stress"].mean()
    avg_rubber = df["rubber_mm"].mean()
    avg_temp = df["temperature_C"].mean()
    avg_humidity = df["humidity_pct"].mean()
    
    # Maintenance recommendations
    urgent_zones = [z["zone"] for z in zone_summaries if z["status"] == "critical"]
    inspect_zones = [z["zone"] for z in zone_summaries if z["status"] == "high"]
    
    return AnalyticsSummary(
        total_flights=total_flights,
        anomaly_rate=round(anomaly_rate, 2),
        worst_zone=worst_zone["zone"],
        worst_zone_status=worst_zone["status"],
        avg_stress=round(avg_stress, 2),
        avg_rubber=round(avg_rubber, 2),
        avg_temperature=round(avg_temp, 1),
        avg_humidity=round(avg_humidity, 1),
        maintenance_urgent_zones=urgent_zones,
        maintenance_inspect_zones=inspect_zones
    )


@router.get("/zones", response_model=List[ZoneSummary])
async def get_zones():
    """Get summary for all zones."""
    df = load_data()
    summaries = get_zone_summary(df)
    return [ZoneSummary(**s) for s in summaries]


@router.get("/timeseries", response_model=TimeSeriesData)
async def get_timeseries(metric: str, zone: Optional[int] = None):
    """Get time series data for a metric."""
    df = load_data()
    data = get_time_series(df, metric, zone)
    return TimeSeriesData(**data)


@router.get("/heatmap", response_model=HeatmapData)
async def get_heatmap():
    """Get zone × metric heatmap."""
    df = load_data()
    data = get_heatmap_data(df)
    return HeatmapData(**data)

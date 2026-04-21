"""
Pydantic data models for SmartZone-R API.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FlightRecord(BaseModel):
    """Single flight record."""
    timestamp: str
    flight_id: str
    aircraft: str
    zone: int
    rubber_mm: float
    cracks_mm: float
    water_mm: float
    stress: float
    fod_weight_g: float
    temperature_C: float
    humidity_pct: float
    rain_mm: float
    anomaly: int


class ZoneSummary(BaseModel):
    """Summary statistics for a runway zone."""
    zone: int
    avg_stress: float
    max_stress: float
    avg_rubber: float
    avg_cracks: float
    avg_water: float
    avg_fod: float
    flight_count: int
    anomaly_count: int
    status: str  # "normal", "high", "critical"


class AlertRecord(BaseModel):
    """An alert triggered by thresholds."""
    timestamp: str
    flight_id: str
    aircraft: str
    zone: int
    severity: str  # "normal", "medium", "high", "critical"
    reasons: List[str]
    stress: float
    rubber_mm: float
    cracks_mm: float
    water_mm: float
    fod_weight_g: float


class AlertSummary(BaseModel):
    """Count of alerts by severity."""
    critical: int
    high: int
    medium: int
    normal: int
    total: int


class SystemStatus(BaseModel):
    """Overall system health status."""
    db_connected: bool
    csv_connected: bool
    last_update: str
    total_zones: int
    total_flights: int
    active_alerts: int
    uptime_seconds: float
    airport_code: str = "MAA"


class AnalyticsSummary(BaseModel):
    """High-level analytics overview."""
    total_flights: int
    anomaly_rate: float
    worst_zone: int
    worst_zone_status: str
    avg_stress: float
    avg_rubber: float
    avg_temperature: float
    avg_humidity: float
    maintenance_urgent_zones: List[int]
    maintenance_inspect_zones: List[int]


class TimeSeriesData(BaseModel):
    """Time series data for charting."""
    labels: List[str]
    datasets: List[dict]


class HeatmapData(BaseModel):
    """Zone × Metric heatmap."""
    zones: List[int]
    metrics: List[str]
    data: List[List[float]]

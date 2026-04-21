"""
Flight data endpoints for SmartZone-R API.
"""

from typing import List, Optional
from fastapi import APIRouter
from models import FlightRecord
from database import load_data, get_recent_flights, get_flights_by_zone

router = APIRouter(prefix="/api/flights", tags=["flights"])


@router.get("", response_model=List[FlightRecord])
async def get_flights(zone: Optional[int] = None):
    """Get recent flights, optionally filtered by zone."""
    df = load_data()
    
    if zone is not None:
        flights = get_flights_by_zone(df, zone, n=50)
    else:
        flights = get_recent_flights(df, n=50)
    
    return flights


@router.get("/zone/{zone}", response_model=List[FlightRecord])
async def get_flights_for_zone(zone: int):
    """Get recent flights for a specific zone."""
    df = load_data()
    flights = get_flights_by_zone(df, zone, n=20)
    return flights


@router.get("/latest", response_model=Optional[FlightRecord])
async def get_latest_flight():
    """Get the most recent flight record."""
    df = load_data()
    flights = get_recent_flights(df, n=1)
    return flights[0] if flights else None

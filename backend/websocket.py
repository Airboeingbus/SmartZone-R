"""
WebSocket real-time updates for SmartZone-R
Broadcasts zone status, alerts, and KPIs to connected clients
"""

import asyncio
import json
import logging
from typing import Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, status
from database import get_db_connection, execute_query

logger = logging.getLogger(__name__)

MAX_CONNECTIONS = 50
PUSH_INTERVAL_SECONDS = 2


class ConnectionManager:
    """Manage WebSocket connections and broadcasting"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket) -> bool:
        """Accept new WebSocket connection"""
        if len(self.active_connections) >= MAX_CONNECTIONS:
            return False

        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")
        return True

    async def disconnect(self, websocket: WebSocket):
        """Remove disconnected client"""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = set()

        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending to client: {e}")
                disconnected.add(connection)
                try:
                    await connection.close(code=status.WS_1011_SERVER_ERROR)
                except Exception:
                    pass

        # Clean up disconnected clients
        for conn in disconnected:
            await self.disconnect(conn)

    async def start_broadcast(self):
        """Start periodic broadcast of zone status and KPIs"""
        while True:
            try:
                # Wait for next push interval
                await asyncio.sleep(PUSH_INTERVAL_SECONDS)

                # Skip if no connected clients
                if not self.active_connections:
                    continue

                # Fetch current data from database
                message = await self._build_live_update()

                # Broadcast to all clients
                if message:
                    await self.broadcast(message)

            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                await asyncio.sleep(PUSH_INTERVAL_SECONDS)

    async def stop_broadcast(self):
        """Stop periodic broadcasts"""
        if self.broadcast_task:
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass

    async def _build_live_update(self) -> Optional[dict]:
        """Build live update message with current zone status and KPIs"""
        try:
            with get_db_connection() as conn:
                # Get latest readings by zone
                zones_query = """
                SELECT zo.zone_id, zo.zone_name,
                       AVG(rd.stress) as avg_stress,
                       AVG(rd.rubber_mm) as avg_rubber,
                       MAX(rd.temperature_C) as max_temp,
                       MAX(rd.humidity_pct) as max_humidity,
                       COUNT(*) as reading_count,
                       COUNT(CASE WHEN rd.anomaly = 1 THEN 1 END) as anomaly_count
                FROM zones zo
                LEFT JOIN runway_data rd ON zo.zone_id = rd.zone_id
                WHERE rd.timestamp > datetime('now', '-1 hour')
                GROUP BY zo.zone_id, zo.zone_name
                ORDER BY zo.zone_id
                """
                zones = execute_query(zones_query, fetch_all=True)

                # Format zones data
                zones_status = {}
                for zone in zones:
                    zone_dict = dict(zone)
                    status_str = "NORMAL"

                    if zone_dict.get("avg_stress", 0) > 80:
                        status_str = "CRITICAL"
                    elif zone_dict.get("avg_stress", 0) > 60:
                        status_str = "WARNING"
                    elif zone_dict.get("anomaly_count", 0) > 0:
                        status_str = "ANOMALY"

                    zones_status[zone_dict["zone_id"]] = {
                        "name": zone_dict.get("zone_name", f"Zone {zone_dict['zone_id']}"),
                        "status": status_str,
                        "avg_stress": round(zone_dict.get("avg_stress", 0), 2),
                        "avg_rubber": round(zone_dict.get("avg_rubber", 0), 2),
                        "max_temp": zone_dict.get("max_temp", 0),
                        "max_humidity": zone_dict.get("max_humidity", 0),
                        "anomalies": zone_dict.get("anomaly_count", 0),
                    }

                # Get active alerts count
                alerts_query = """
                SELECT resolved,
                       COUNT(*) as count
                FROM alerts
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY resolved
                """
                alerts_result = execute_query(alerts_query, fetch_all=True)
                active_alerts = 0
                for alert in alerts_result:
                    if dict(alert).get("resolved") == 0:
                        active_alerts = dict(alert).get("count", 0)

                # Get overall KPIs
                kpis_query = """
                SELECT COUNT(DISTINCT flight_id) as total_flights,
                       COUNT(CASE WHEN anomaly = 1 THEN 1 END) as anomalies,
                       AVG(stress) as avg_stress,
                       AVG(rubber_mm) as avg_rubber,
                       MAX(stress) as max_stress
                FROM runway_data
                WHERE timestamp > datetime('now', '-1 hour')
                """
                kpis = dict(execute_query(kpis_query, fetch_one=True))

                # Find worst zone
                worst_zone = "Zone-01"
                worst_stress = 0
                for zone_id, zone_data in zones_status.items():
                    if zone_data["avg_stress"] > worst_stress:
                        worst_stress = zone_data["avg_stress"]
                        worst_zone = zone_data["name"]

                # Build message
                message = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "live_update",
                    "zones": zones_status,
                    "active_alerts": active_alerts,
                    "kpis": {
                        "flights": kpis.get("total_flights", 0),
                        "anomalies": kpis.get("anomalies", 0),
                        "worst_zone": worst_zone,
                        "avg_stress": round(kpis.get("avg_stress", 0), 2),
                        "avg_rubber": round(kpis.get("avg_rubber", 0), 2),
                        "max_stress": round(kpis.get("max_stress", 0), 2),
                    },
                }

                return message

        except Exception as e:
            logger.error(f"Error building live update: {e}")
            return None


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint with token authentication"""
    from auth import AuthToken

    # Verify token before accepting connection
    try:
        payload = AuthToken.verify_token(token)
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    # Accept connection
    connected = await manager.connect(websocket)
    if not connected:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Max connections reached")
        return

    try:
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back or handle commands if needed
            logger.debug(f"WebSocket message: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)


async def start_websocket_broadcaster():
    """Start the background broadcast task"""
    manager.broadcast_task = asyncio.create_task(manager.start_broadcast())
    logger.info("WebSocket broadcaster started")


async def stop_websocket_broadcaster():
    """Stop the background broadcast task"""
    await manager.stop_broadcast()
    logger.info("WebSocket broadcaster stopped")

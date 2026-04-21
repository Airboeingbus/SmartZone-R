"""
SmartZone-R FastAPI Server
Main entry point for the API backend.
"""

import os
import sys
import logging
from typing import Optional
from fastapi import FastAPI, WebSocket, Query, Body, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure backend directory is in path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes import status, flights, analytics, alerts
from serial_listener import start_serial_listener, stop_serial_listener, get_listener_status
from auth import Authentication, AuthToken
from websocket import websocket_endpoint, start_websocket_broadcaster, stop_websocket_broadcaster

# Pydantic models for request/response validation
class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    access_token: str

# Role-based access control dependency
async def get_current_user(request: Request):
    """Extract and verify JWT token from request."""
    try:
        token = Authentication.get_token_from_header(request)
        payload = AuthToken.verify_token(token)
        return {
            "username": payload.get("username"),
            "role": payload.get("role"),
            "token": token
        }
    except HTTPException:
        raise

def require_role(*allowed_roles: str):
    """Dependency to enforce role-based access control."""
    async def check_role(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="INSUFFICIENT CLEARANCE"
            )
        return current_user
    return check_role

# Create FastAPI app
app = FastAPI(
    title="SmartZone-R API",
    description="Runway Monitoring System API",
    version="1.0.0"
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event - start background services
@app.on_event("startup")
async def startup_event():
    """Start background services on app startup."""
    logger.info("Starting SmartZone-R services...")
    start_serial_listener()
    await start_websocket_broadcaster()
    logger.info("Services started successfully")

# Shutdown event - stop background services
@app.on_event("shutdown")
async def shutdown_event():
    """Stop background services on app shutdown."""
    logger.info("Stopping SmartZone-R services...")
    stop_serial_listener()
    await stop_websocket_broadcaster()
    logger.info("Services stopped")

# Include API route modules FIRST (priority)
app.include_router(status.router)
app.include_router(flights.router)
app.include_router(analytics.router)
app.include_router(alerts.router)

# Authentication Endpoints
@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    """Login endpoint - returns JWT token."""
    try:
        result = Authentication.login(credentials.username, credentials.password)
        logger.info(f"User {credentials.username} logged in")
        return result
    except HTTPException:
        logger.warning(f"Failed login attempt for user {credentials.username}")
        raise

@app.post("/api/auth/refresh")
async def refresh_token(token_data: RefreshRequest):
    """Refresh JWT token if expiring soon."""
    try:
        result = Authentication.refresh(token_data.access_token)
        return result
    except HTTPException:
        raise

@app.get("/api/auth/me")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info."""
    return {
        "username": current_user["username"],
        "role": current_user["role"],
    }

# WebSocket Endpoint
@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket, token: str = Query(None)):
    """WebSocket endpoint for live updates with token authentication."""
    await websocket_endpoint(websocket, token)

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SmartZone-R API"
    }

# Hardware status endpoint
@app.get("/api/hardware/status")
async def hardware_status():
    """Get ESP32 serial listener status and hardware connection info."""
    status_info = get_listener_status()
    return {
        "connected": status_info["connected"],
        "port": status_info["port"],
        "last_reading": status_info["last_reading"],
        "total_inserted": status_info["total_inserted"],
        "service": "Serial Listener"
    }

# Determine frontend path
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
frontend_dir = Path(frontend_path)

# Serve index.html at root
@app.get("/")
async def root():
    """Serve main dashboard."""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    return {"error": "Frontend files not found"}

# Serve login.html
@app.get("/login")
async def serve_login():
    """Serve login page."""
    login_file = frontend_dir / "login.html"
    if login_file.exists():
        return FileResponse(login_file, media_type="text/html")
    return {"error": "Login page not found"}

# Serve all other files (LAST - catch-all for frontend files)
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend files. Skip /api routes (handled by routers above)."""
    # Skip API routes - they're handled by the routers
    if path.startswith("api/"):
        return {"error": "API endpoint not found"}
    
    # Skip WebSocket routes
    if path.startswith("ws/"):
        return {"error": "WebSocket endpoint not found"}
    
    # Try exact file first
    file_path = frontend_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Try with .html
    html_path = frontend_dir / f"{path}.html"
    if html_path.exists() and html_path.is_file():
        return FileResponse(html_path, media_type="text/html")
    
    # Default to index.html for unknown routes
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    
    return {"error": "File not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

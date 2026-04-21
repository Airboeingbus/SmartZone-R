"""
Authentication & Authorization module for SmartZone-R
JWT-based RBAC with role-based endpoint protection
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from fastapi import HTTPException, status, Request
from dotenv import load_dotenv

load_dotenv()

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET must be set in .env file")

JWT_EXPIRY_HOURS = 8
REFRESH_WINDOW_HOURS = 1

# Credentials from .env only
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
MAINTENANCE_PASSWORD = os.getenv("MAINTENANCE_PASSWORD")
VIEWER_PASSWORD = os.getenv("VIEWER_PASSWORD")

# Role definitions
ROLES = {
    "admin": ["read", "write", "download", "configure"],
    "maintenance": ["read", "download"],
    "viewer": ["read"],
}

class AuthToken:
    """JWT token management"""

    @staticmethod
    def create_token(username: str, role: str) -> str:
        """Create JWT token with expiry"""
        payload = {
            "username": username,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def is_token_expiring_soon(token: str) -> bool:
        """Check if token expires within REFRESH_WINDOW_HOURS"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            exp_time = datetime.fromtimestamp(payload["exp"])
            refresh_window = datetime.utcnow() + timedelta(hours=REFRESH_WINDOW_HOURS)
            return exp_time < refresh_window
        except jwt.InvalidTokenError:
            return False


class Authentication:
    """Handle login/logout/refresh flows"""

    @staticmethod
    def login(username: str, password: str) -> dict:
        """Validate credentials and return JWT token"""
        role = None

        if username == "admin" and password == ADMIN_PASSWORD:
            role = "admin"
        elif username == "maintenance" and password == MAINTENANCE_PASSWORD:
            role = "maintenance"
        elif username == "viewer" and password == VIEWER_PASSWORD:
            role = "viewer"
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        token = AuthToken.create_token(username, role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": username,
            "role": role,
            "expires_in": JWT_EXPIRY_HOURS * 3600,  # seconds
        }

    @staticmethod
    def refresh(token: str) -> dict:
        """Issue new token if current one is expiring"""
        payload = AuthToken.verify_token(token)

        if not AuthToken.is_token_expiring_soon(token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token not expiring soon",
            )

        new_token = AuthToken.create_token(payload["username"], payload["role"])
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "username": payload["username"],
            "role": payload["role"],
            "expires_in": JWT_EXPIRY_HOURS * 3600,
        }

    @staticmethod
    def get_token_from_header(request: Request) -> str:
        """Extract token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
            )

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )

        return parts[1]


def require_auth(required_role: str = None):
    """Decorator to protect FastAPI endpoints with auth"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            try:
                # Get token from header
                token = Authentication.get_token_from_header(request)

                # Verify token
                payload = AuthToken.verify_token(token)
                user_role = payload.get("role")

                # Check role permissions
                if required_role and required_role not in ROLES.get(user_role, []):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role '{user_role}' does not have permission",
                    )

                # Inject user info into kwargs
                kwargs["current_user"] = {
                    "username": payload.get("username"),
                    "role": user_role,
                }

                return await func(*args, request=request, **kwargs)

            except HTTPException:
                raise

        return wrapper

    return decorator


def require_auth_sync(required_role: str = None):
    """Decorator for sync functions (non-async)"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, request: Request = None, **kwargs):
            try:
                # Get token from header
                token = Authentication.get_token_from_header(request)

                # Verify token
                payload = AuthToken.verify_token(token)
                user_role = payload.get("role")

                # Check role permissions
                if required_role and required_role not in ROLES.get(user_role, []):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role '{user_role}' does not have permission",
                    )

                # Inject user info into kwargs
                kwargs["current_user"] = {
                    "username": payload.get("username"),
                    "role": user_role,
                }

                return func(*args, request=request, **kwargs)

            except HTTPException:
                raise

        return wrapper

    return decorator

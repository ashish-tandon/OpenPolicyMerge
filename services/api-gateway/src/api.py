"""
API endpoints for API Gateway Service
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
from .config import Config

router = APIRouter()

@router.get("/api/gateway/status")
async def gateway_status():
    """API Gateway service status"""
    return {
        "status": "active",
        "service": Config.SERVICE_NAME,
        "version": Config.SERVICE_VERSION,
        "port": Config.SERVICE_PORT,
        "features": {
            "rate_limiting": Config.ENABLE_RATE_LIMITING,
            "caching": Config.ENABLE_CACHING,
            "logging": Config.ENABLE_LOGGING
        }
    }

@router.get("/api/gateway/routes")
async def get_routes():
    """Get available API routes"""
    return {
        "routes": [
            {"path": "/api/auth", "service": "auth-service", "port": 9003},
            {"path": "/api/policy", "service": "policy-service", "port": 9001},
            {"path": "/api/search", "service": "search-service", "port": 9002}
        ]
    }

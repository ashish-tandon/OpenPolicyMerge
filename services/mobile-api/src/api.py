"""
API endpoints for Mobile API Service
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
from .config import config

router = APIRouter()

@router.get("/api/mobile/status")
async def mobile_status():
    """Mobile API service status"""
    return {
        "status": "active",
        "service": config.SERVICE_NAME,
        "version": config.SERVICE_VERSION,
        "port": config.SERVICE_PORT,
        "features": {
            "push_notifications": config.ENABLE_PUSH_NOTIFICATIONS,
            "offline_mode": config.ENABLE_OFFLINE_MODE,
            "rate_limiting": config.ENABLE_RATE_LIMITING
        }
    }

@router.get("/api/mobile/config")
async def get_mobile_config():
    """Get mobile API configuration"""
    return {
        "offline_data_limit": config.MAX_OFFLINE_DATA,
        "sync_interval": config.SYNC_INTERVAL,
        "rate_limit": {
            "enabled": config.ENABLE_RATE_LIMITING,
            "window_ms": config.RATE_LIMIT_WINDOW_MS,
            "max_requests": config.RATE_LIMIT_MAX
        }
    }

@router.get("/api/mobile/features")
async def get_mobile_features():
    """Get available mobile features"""
    return {
        "features": {
            "push_notifications": config.ENABLE_PUSH_NOTIFICATIONS,
            "offline_mode": config.ENABLE_OFFLINE_MODE,
            "authentication": config.ENABLE_AUTH,
            "compression": config.ENABLE_COMPRESSION,
            "caching": config.ENABLE_CACHING
        }
    }

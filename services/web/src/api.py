"""
API endpoints for Web Frontend Service
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
from .config import Config

router = APIRouter()

@router.get("/api/web/status")
async def web_status():
    """Web frontend service status"""
    return {
        "status": "active",
        "service": Config.SERVICE_NAME,
        "version": Config.SERVICE_VERSION,
        "port": Config.SERVICE_PORT,
        "features": {
            "dark_mode": Config.ENABLE_DARK_MODE,
            "analytics": Config.ENABLE_ANALYTICS,
            "pwa": Config.ENABLE_PWA,
            "ssr": Config.ENABLE_SSR
        }
    }

@router.get("/api/web/config")
async def get_web_config():
    """Get web frontend configuration"""
    return {
        "theme": Config.PLOTLY_THEME,
        "api_url": Config.NEXT_PUBLIC_API_URL,
        "app_name": Config.NEXT_PUBLIC_APP_NAME,
        "app_description": Config.NEXT_PUBLIC_APP_DESCRIPTION
    }

@router.get("/api/web/features")
async def get_web_features():
    """Get available web features"""
    return {
        "features": {
            "authentication": Config.ENABLE_AUTH,
            "dark_mode": Config.ENABLE_DARK_MODE,
            "analytics": Config.ENABLE_ANALYTICS,
            "pwa": Config.ENABLE_PWA,
            "ssr": Config.ENABLE_SSR
        }
    }

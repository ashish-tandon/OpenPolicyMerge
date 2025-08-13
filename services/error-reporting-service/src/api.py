"""
API endpoints for Error Reporting Service
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
from .config import Config

router = APIRouter()

@router.get("/api/errors/status")
async def error_service_status():
    """Error reporting service status"""
    return {
        "status": "active",
        "service": Config.SERVICE_NAME,
        "version": Config.SERVICE_VERSION,
        "port": Config.SERVICE_PORT,
        "features": {
            "real_time_monitoring": Config.ENABLE_REAL_TIME_MONITORING,
            "error_aggregation": Config.ENABLE_ERROR_AGGREGATION,
            "alerts": Config.ENABLE_ALERTS
        }
    }

@router.post("/api/errors/report")
async def report_error(error_data: dict):
    """Report an error to the service"""
    return {
        "status": "error_reported",
        "timestamp": datetime.utcnow().isoformat(),
        "service": Config.SERVICE_NAME,
        "error_id": f"err_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    }

@router.post("/api/errors/log")
async def report_log(log_data: dict):
    """Report a log entry to the service"""
    return {
        "status": "log_reported",
        "timestamp": datetime.utcnow().isoformat(),
        "service": Config.SERVICE_NAME,
        "log_id": f"log_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    }

@router.get("/api/errors/alerts")
async def get_alerts():
    """Get current error alerts"""
    return {
        "alerts": [],
        "total_count": 0
    }

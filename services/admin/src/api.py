"""
API endpoints for Admin Dashboard Service
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
from .config import config

router = APIRouter()

@router.get("/api/admin/status")
async def admin_status():
    """Admin service status"""
    return {
        "status": "active",
        "service": config.SERVICE_NAME,
        "version": config.SERVICE_VERSION,
        "port": config.SERVICE_PORT,
        "features": {
            "user_management": config.ENABLE_USER_MANAGEMENT,
            "service_management": config.ENABLE_SERVICE_MANAGEMENT,
            "system_monitoring": config.ENABLE_SYSTEM_MONITORING,
            "audit_logs": config.ENABLE_AUDIT_LOGS,
            "backup_restore": config.ENABLE_BACKUP_RESTORE
        }
    }

@router.get("/api/admin/dashboard")
async def get_dashboard_data():
    """Get admin dashboard data"""
    return {
        "overview": {
            "total_services": 25,
            "healthy_services": 20,
            "unhealthy_services": 5,
            "total_users": 0
        },
        "system_metrics": {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": 0.0
        },
        "recent_activities": [],
        "alerts": []
    }

@router.get("/api/admin/users")
async def list_users():
    """List all users"""
    return {
        "users": [],
        "total_count": 0
    }

@router.get("/api/admin/services")
async def list_services():
    """List all platform services"""
    return {
        "services": [],
        "total_count": 25
    }

@router.get("/api/admin/logs")
async def get_logs():
    """Get system logs"""
    return {
        "logs": [],
        "total_count": 0
    }

"""
API endpoints for MCP Service
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
from .config import Config

router = APIRouter()

@router.get("/api/mcp/status")
async def mcp_service_status():
    """MCP service status"""
    return {
        "status": "active",
        "service": Config.SERVICE_NAME,
        "version": Config.SERVICE_VERSION,
        "port": Config.SERVICE_PORT
    }

@router.get("/api/mcp/health")
async def mcp_health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": Config.SERVICE_NAME
    }

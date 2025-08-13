"""
API endpoints for OP Import Service
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter()

@router.get("/api/op-import/status")
async def op_import_status():
    """OP Import service status"""
    return {
        "status": "active",
        "service": "op-import",
        "version": "1.0.0",
        "port": 9023
    }

@router.get("/api/op-import/health")
async def op_import_health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "op-import"
    }

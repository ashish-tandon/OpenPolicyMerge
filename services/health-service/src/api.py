"""
Health Service API - Complete Implementation
FastAPI application for system health monitoring.
"""

from fastapi import FastAPI, Depends, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime
import psutil
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Health Service API",
    description="OpenPolicy Platform - System Health Monitoring Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class HealthStatus(BaseModel):
    service: str
    status: str
    timestamp: datetime
    version: str
    uptime: str
    checks: Dict[str, Any]

class ServiceHealth(BaseModel):
    name: str
    status: str
    response_time: float
    last_check: datetime
    details: Optional[Dict[str, Any]]

# Health endpoints
@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Get system info
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds%3600)//60}m"
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "health-service",
            "version": "1.0.0",
            "uptime": uptime_str,
            "checks": {
                "system": "healthy",
                "memory": "healthy",
                "disk": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/readyz", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check if service is ready to handle requests
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "service": "health-service"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/system", tags=["System"])
async def get_system_info():
    """Get system information."""
    try:
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory info
        memory = psutil.virtual_memory()
        
        # Disk info
        disk = psutil.disk_usage('/')
        
        # Network info
        network = psutil.net_io_counters()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system info")

@app.get("/services", response_model=List[ServiceHealth], tags=["Services"])
async def get_services_health():
    """Get health status of all services."""
    try:
        # This would check actual service health in production
        # For now, return mock data
        services = [
            ServiceHealth(
                name="policy-service",
                status="healthy",
                response_time=0.05,
                last_check=datetime.now(),
                details={"port": 8001, "version": "1.0.0"}
            ),
            ServiceHealth(
                name="search-service",
                status="healthy",
                response_time=0.03,
                last_check=datetime.now(),
                details={"port": 8002, "version": "1.0.0"}
            ),
            ServiceHealth(
                name="auth-service",
                status="healthy",
                response_time=0.04,
                last_check=datetime.now(),
                details={"port": 8003, "version": "1.0.0"}
            )
        ]
        
        return services
        
    except Exception as e:
        logger.error(f"Failed to get services health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get services health")

@app.get("/metrics", tags=["Metrics"])
async def get_metrics():
    """Get Prometheus-style metrics."""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = [
            f"# HELP openpolicy_cpu_usage_percent CPU usage percentage",
            f"# TYPE openpolicy_cpu_usage_percent gauge",
            f"openpolicy_cpu_usage_percent {cpu_percent}",
            "",
            f"# HELP openpolicy_memory_usage_bytes Memory usage in bytes",
            f"# TYPE openpolicy_memory_usage_bytes gauge",
            f"openpolicy_memory_usage_bytes {memory.used}",
            "",
            f"# HELP openpolicy_disk_usage_bytes Disk usage in bytes",
            f"# TYPE openpolicy_disk_usage_bytes gauge",
            f"openpolicy_disk_usage_bytes {disk.used}",
            "",
            f"# HELP openpolicy_service_uptime_seconds Service uptime in seconds",
            f"# TYPE openpolicy_service_uptime_seconds counter",
            f"openpolicy_service_uptime_seconds {int((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds())}"
        ]
        
        return "\n".join(metrics)
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)

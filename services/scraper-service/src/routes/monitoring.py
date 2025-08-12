"""
Monitoring routes for OpenPolicy Scraper Service
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from src.core.models import (
    HealthStatus, MetricsSummary, Alert, 
    ScraperStatus, JobStatus
)
from src.services.scraper_manager import ScraperManager
from src.core.monitoring import get_metrics

router = APIRouter()

# Global scraper manager instance
scraper_manager = None

@router.on_event("startup")
async def startup_event():
    """Initialize scraper manager on startup"""
    global scraper_manager
    scraper_manager = ScraperManager()

@router.get("/health", response_model=HealthStatus)
async def get_health():
    """Get comprehensive health status"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        # Get basic health info
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "uptime": 0.0,  # Will be calculated
            "services": {},
            "dependencies": {}
        }
        
        # Check scraper manager health
        try:
            scraper_health = await scraper_manager.get_health()
            health_status["services"]["scraper_manager"] = scraper_health["status"]
            if scraper_health["status"] != "healthy":
                health_status["status"] = "unhealthy"
        except Exception as e:
            health_status["services"]["scraper_manager"] = f"error: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check database health
        try:
            db_health = await scraper_manager.check_database_health()
            health_status["dependencies"]["database"] = db_health["status"]
            if db_health["status"] != "healthy":
                health_status["status"] = "unhealthy"
        except Exception as e:
            health_status["dependencies"]["database"] = f"error: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check Redis health
        try:
            redis_health = await scraper_manager.check_redis_health()
            health_status["dependencies"]["redis"] = redis_health["status"]
            if redis_health["status"] != "healthy":
                health_status["status"] = "unhealthy"
        except Exception as e:
            health_status["dependencies"]["redis"] = f"error: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Calculate uptime (simplified)
        health_status["uptime"] = 0.0  # Will be implemented with actual start time
        
        return HealthStatus(**health_status)
        
    except Exception as e:
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            uptime=0.0,
            services={"error": str(e)},
            dependencies={}
        )

@router.get("/metrics")
async def get_prometheus_metrics():
    """Get Prometheus metrics"""
    try:
        metrics = get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary():
    """Get summary metrics"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        summary = await scraper_manager.get_metrics_summary()
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts", response_model=List[Alert])
async def get_alerts(
    level: str = None,
    acknowledged: bool = None,
    limit: int = 100
):
    """Get alerts with optional filtering"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        alerts = await scraper_manager.get_alerts(level, acknowledged, limit)
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        success = await scraper_manager.acknowledge_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        return {"message": f"Alert {alert_id} acknowledged successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_service_logs(
    level: str = "info",
    limit: int = 100,
    start_date: datetime = None,
    end_date: datetime = None
):
    """Get service logs"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        logs = await scraper_manager.get_service_logs(level, limit, start_date, end_date)
        return logs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics(
    scraper_name: str = None,
    start_date: datetime = None,
    end_date: datetime = None
):
    """Get performance metrics"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        metrics = await scraper_manager.get_performance_metrics(scraper_name, start_date, end_date)
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scrapers/status")
async def get_all_scrapers_status():
    """Get status of all scrapers"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        status = await scraper_manager.get_all_scrapers_status()
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/status")
async def get_all_jobs_status():
    """Get status of all jobs"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        status = await scraper_manager.get_all_jobs_status()
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/resources")
async def get_system_resources():
    """Get system resource usage"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        resources = await scraper_manager.get_system_resources()
        return resources
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/processes")
async def get_system_processes():
    """Get system process information"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        processes = await scraper_manager.get_system_processes()
        return processes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance/cleanup")
async def run_maintenance_cleanup():
    """Run maintenance cleanup tasks"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        result = await scraper_manager.run_maintenance_cleanup()
        return {
            "message": "Maintenance cleanup completed successfully",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance/optimize")
async def run_maintenance_optimize():
    """Run maintenance optimization tasks"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        result = await scraper_manager.run_maintenance_optimize()
        return {
            "message": "Maintenance optimization completed successfully",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

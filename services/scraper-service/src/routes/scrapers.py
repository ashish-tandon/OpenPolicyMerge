"""
Scrapers routes for OpenPolicy Scraper Service
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
import asyncio

from src.core.models import (
    ScraperInfo, ScraperRunRequest, ScraperRunResponse, 
    ScraperConfiguration, ScraperStatus, ScraperPriority
)
from src.services.scraper_manager import ScraperManager
from src.core.monitoring import record_scraper_request, record_data_collected

router = APIRouter()

# Global scraper manager instance
scraper_manager = None

@router.on_event("startup")
async def startup_event():
    """Initialize scraper manager on startup"""
    global scraper_manager
    scraper_manager = ScraperManager()

@router.get("/", response_model=List[ScraperInfo])
async def get_scrapers():
    """Get list of all available scrapers"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        scrapers = await scraper_manager.get_all_scrapers()
        return scrapers
        
    except Exception as e:
        record_scraper_request("scrapers", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scraper_name}", response_model=ScraperInfo)
async def get_scraper(scraper_name: str):
    """Get information about a specific scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        scraper = await scraper_manager.get_scraper(scraper_name)
        if not scraper:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        return scraper
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{scraper_name}/run", response_model=ScraperRunResponse)
async def run_scraper(
    scraper_name: str,
    request: ScraperRunRequest,
    background_tasks: BackgroundTasks
):
    """Run a specific scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        # Validate scraper exists
        scraper = await scraper_manager.get_scraper(scraper_name)
        if not scraper:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        # Check if scraper is enabled
        if not scraper.get("enabled", False) and not request.force:
            raise HTTPException(status_code=400, detail=f"Scraper {scraper_name} is disabled")
        
        # Run scraper in background
        job_id = await scraper_manager.run_scraper(scraper_name, request.force, request.parameters)
        
        record_scraper_request(scraper_name, "success")
        
        return ScraperRunResponse(
            scraper_name=scraper_name,
            job_id=job_id,
            status="pending",
            message=f"Scraper {scraper_name} started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{scraper_name}/enable")
async def enable_scraper(scraper_name: str):
    """Enable a specific scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        success = await scraper_manager.enable_scraper(scraper_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        record_scraper_request(scraper_name, "success")
        return {"message": f"Scraper {scraper_name} enabled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{scraper_name}/disable")
async def disable_scraper(scraper_name: str):
    """Disable a specific scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        success = await scraper_manager.disable_scraper(scraper_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        record_scraper_request(scraper_name, "success")
        return {"message": f"Scraper {scraper_name} disabled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scraper_name}/status")
async def get_scraper_status(scraper_name: str):
    """Get current status of a specific scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        status = await scraper_manager.get_scraper_status(scraper_name)
        if not status:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scraper_name}/data")
async def get_scraper_data(
    scraper_name: str,
    limit: int = 100,
    offset: int = 0
):
    """Get data collected by a specific scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        data = await scraper_manager.get_scraper_data(scraper_name, limit, offset)
        if data is None:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        record_data_collected(scraper_name, "data_retrieval")
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{scraper_name}/config")
async def update_scraper_config(
    scraper_name: str,
    config: ScraperConfiguration
):
    """Update configuration for a specific scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        success = await scraper_manager.update_scraper_config(scraper_name, config.config)
        if not success:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        record_scraper_request(scraper_name, "success")
        return {"message": f"Configuration updated for scraper {scraper_name}"}
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scraper_name}/logs")
async def get_scraper_logs(
    scraper_name: str,
    limit: int = 100,
    level: str = "info"
):
    """Get logs for a specific scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        logs = await scraper_manager.get_scraper_logs(scraper_name, limit, level)
        if logs is None:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        return logs
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{scraper_name}/test")
async def test_scraper(scraper_name: str):
    """Test a specific scraper without collecting data"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        result = await scraper_manager.test_scraper(scraper_name)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Scraper {scraper_name} not found")
        
        record_scraper_request(scraper_name, "success")
        return {
            "scraper_name": scraper_name,
            "test_result": result,
            "message": f"Test completed for scraper {scraper_name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request(scraper_name, "error")
        raise HTTPException(status_code=500, detail=str(e))

"""
Jobs routes for OpenPolicy Scraper Service
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from src.core.models import (
    ScraperJob, JobCreateRequest, JobUpdateRequest, 
    JobStatus, ScraperPriority, PaginatedResponse
)
from src.services.scraper_manager import ScraperManager
from src.core.monitoring import record_scraper_request

router = APIRouter()

# Global scraper manager instance
scraper_manager = None

@router.on_event("startup")
async def startup_event():
    """Initialize scraper manager on startup"""
    global scraper_manager
    scraper_manager = ScraperManager()

@router.get("/", response_model=PaginatedResponse)
async def get_jobs(
    status: Optional[JobStatus] = None,
    scraper_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get list of all jobs with optional filtering"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        jobs = await scraper_manager.get_jobs(status, scraper_name, limit, offset)
        total = await scraper_manager.get_jobs_count(status, scraper_name)
        
        return PaginatedResponse(
            data=jobs,
            total=total,
            page=(offset // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
        
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}", response_model=ScraperJob)
async def get_job(job_id: str):
    """Get information about a specific job"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        job = await scraper_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ScraperJob)
async def create_job(request: JobCreateRequest):
    """Create a new job"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        job = await scraper_manager.create_job(
            scraper_name=request.scraper_name,
            parameters=request.parameters,
            priority=request.priority,
            schedule_at=request.schedule_at
        )
        
        if not job:
            raise HTTPException(status_code=400, detail="Failed to create job")
        
        record_scraper_request(request.scraper_name, "success")
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{job_id}", response_model=ScraperJob)
async def update_job(job_id: str, request: JobUpdateRequest):
    """Update a job"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        job = await scraper_manager.update_job(
            job_id=job_id,
            status=request.status,
            priority=request.priority,
            parameters=request.parameters
        )
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a job"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        success = await scraper_manager.delete_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return {"message": f"Job {job_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        success = await scraper_manager.cancel_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return {"message": f"Job {job_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}/logs")
async def get_job_logs(
    job_id: str,
    limit: int = 100,
    level: str = "info"
):
    """Get logs for a specific job"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        logs = await scraper_manager.get_job_logs(job_id, limit, level)
        if logs is None:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return logs
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}/stats")
async def get_job_stats(job_id: str):
    """Get statistics for a specific job"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        stats = await scraper_manager.get_job_stats(job_id)
        if stats is None:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_jobs_summary():
    """Get summary statistics for all jobs"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        summary = await scraper_manager.get_jobs_summary()
        return summary
        
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/cancel")
async def cancel_multiple_jobs(job_ids: List[str]):
    """Cancel multiple jobs"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        if not job_ids:
            raise HTTPException(status_code=400, detail="No job IDs specified")
        
        if len(job_ids) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 jobs can be cancelled simultaneously")
        
        results = await scraper_manager.cancel_multiple_jobs(job_ids)
        
        return {
            "message": f"Batch cancel completed: {len(results['successful'])} successful, {len(results['failed'])} failed",
            "successful": results["successful"],
            "failed": results["failed"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("jobs", "error")
        raise HTTPException(status_code=500, detail=str(e))

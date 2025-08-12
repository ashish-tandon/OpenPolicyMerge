"""
Data routes for OpenPolicy Scraper Service
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.core.models import (
    DataRecord, DataQueryRequest, DataExportRequest, 
    DataType, JurisdictionLevel, PaginatedResponse
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

@router.get("/", response_model=PaginatedResponse)
async def get_data(request: DataQueryRequest):
    """Get scraped data with filtering and pagination"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        data = await scraper_manager.get_data(
            scraper_name=request.scraper_name,
            data_type=request.data_type,
            jurisdiction_level=request.jurisdiction_level,
            jurisdiction_name=request.jurisdiction_name,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit,
            offset=request.offset,
            sort_by=request.sort_by,
            sort_order=request.sort_order
        )
        
        total = await scraper_manager.get_data_count(
            scraper_name=request.scraper_name,
            data_type=request.data_type,
            jurisdiction_level=request.jurisdiction_level,
            jurisdiction_name=request.jurisdiction_name,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        record_data_collected("data_retrieval", "query")
        
        return PaginatedResponse(
            data=data,
            total=total,
            page=(request.offset // request.limit) + 1,
            size=request.limit,
            pages=(total + request.limit - 1) // request.limit
        )
        
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{record_id}", response_model=DataRecord)
async def get_data_record(record_id: str):
    """Get a specific data record"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        record = await scraper_manager.get_data_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Data record {record_id} not found")
        
        record_data_collected("data_retrieval", "single_record")
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_data(request: DataExportRequest):
    """Export data in various formats"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        export_data = await scraper_manager.export_data(
            scraper_name=request.scraper_name,
            data_type=request.data_type,
            jurisdiction_level=request.jurisdiction_level,
            start_date=request.start_date,
            end_date=request.end_date,
            format=request.format,
            include_raw=request.include_raw
        )
        
        if not export_data:
            raise HTTPException(status_code=400, detail="No data found for export")
        
        record_data_collected("data_export", request.format)
        
        # Return file response based on format
        if request.format == "csv":
            return {
                "message": "Data exported successfully",
                "format": "csv",
                "records": len(export_data),
                "download_url": f"/api/v1/data/export/{request.format}/download"
            }
        elif request.format == "json":
            return {
                "message": "Data exported successfully",
                "format": "json",
                "records": len(export_data),
                "data": export_data
            }
        else:
            return {
                "message": "Data exported successfully",
                "format": request.format,
                "records": len(export_data)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_data_summary():
    """Get summary statistics for all data"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        summary = await scraper_manager.get_data_summary()
        return summary
        
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/by-scraper")
async def get_data_stats_by_scraper():
    """Get data statistics grouped by scraper"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        stats = await scraper_manager.get_data_stats_by_scraper()
        return stats
        
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/by-jurisdiction")
async def get_data_stats_by_jurisdiction():
    """Get data statistics grouped by jurisdiction"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        stats = await scraper_manager.get_data_stats_by_jurisdiction()
        return stats
        
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/by-type")
async def get_data_stats_by_type():
    """Get data statistics grouped by data type"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        stats = await scraper_manager.get_data_stats_by_type()
        return stats
        
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_data(record_ids: List[str]):
    """Validate specific data records"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        if not record_ids:
            raise HTTPException(status_code=400, detail="No record IDs specified")
        
        if len(record_ids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 records can be validated simultaneously")
        
        validation_results = await scraper_manager.validate_data_records(record_ids)
        
        return {
            "message": f"Data validation completed for {len(record_ids)} records",
            "results": validation_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{record_id}")
async def delete_data_record(record_id: str):
    """Delete a specific data record"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        success = await scraper_manager.delete_data_record(record_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Data record {record_id} not found")
        
        return {"message": f"Data record {record_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/delete")
async def delete_multiple_data_records(record_ids: List[str]):
    """Delete multiple data records"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        if not record_ids:
            raise HTTPException(status_code=400, detail="No record IDs specified")
        
        if len(record_ids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 records can be deleted simultaneously")
        
        results = await scraper_manager.delete_multiple_data_records(record_ids)
        
        return {
            "message": f"Batch delete completed: {len(results['successful'])} successful, {len(results['failed'])} failed",
            "successful": results["successful"],
            "failed": results["failed"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality/report")
async def get_data_quality_report(
    scraper_name: Optional[str] = None,
    jurisdiction_level: Optional[JurisdictionLevel] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get data quality report"""
    try:
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraper manager not initialized")
        
        report = await scraper_manager.get_data_quality_report(
            scraper_name=scraper_name,
            jurisdiction_level=jurisdiction_level,
            start_date=start_date,
            end_date=end_date
        )
        
        return report
        
    except Exception as e:
        record_scraper_request("data", "error")
        raise HTTPException(status_code=500, detail=str(e))

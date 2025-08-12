"""
Charts API Routes for ETL Service

Provides endpoints for creating, managing, and retrieving charts
generated from ETL data processing.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.chart import Chart
from schemas.chart import ChartCreate, ChartUpdate, ChartResponse, ChartList
from services.chart_service import ChartService

router = APIRouter()
chart_service = ChartService()

@router.post("/", response_model=ChartResponse, summary="Create a new chart")
async def create_chart(
    chart_data: ChartCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new chart from ETL data
    
    - **title**: Chart title
    - **chart_type**: Type of chart (line, bar, scatter, etc.)
    - **data_source**: Source of the data
    - **configuration**: Chart configuration and options
    """
    try:
        chart = await chart_service.create_chart(db, chart_data)
        return chart
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=ChartList, summary="List all charts")
async def list_charts(
    skip: int = Query(0, ge=0, description="Number of charts to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of charts to return"),
    chart_type: Optional[str] = Query(None, description="Filter by chart type"),
    data_source: Optional[str] = Query(None, description="Filter by data source"),
    created_after: Optional[datetime] = Query(None, description="Filter charts created after this date"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of charts with optional filtering
    
    - **skip**: Number of charts to skip for pagination
    - **limit**: Maximum number of charts to return
    - **chart_type**: Filter by specific chart type
    - **data_source**: Filter by data source
    - **created_after**: Filter by creation date
    """
    try:
        charts = await chart_service.list_charts(
            db, skip=skip, limit=limit, 
            chart_type=chart_type, data_source=data_source,
            created_after=created_after
        )
        return charts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chart_id}", response_model=ChartResponse, summary="Get chart by ID")
async def get_chart(
    chart_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific chart by its ID
    
    - **chart_id**: Unique identifier of the chart
    """
    try:
        chart = await chart_service.get_chart(db, chart_id)
        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")
        return chart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{chart_id}", response_model=ChartResponse, summary="Update chart")
async def update_chart(
    chart_id: int,
    chart_data: ChartUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing chart
    
    - **chart_id**: Unique identifier of the chart to update
    - **chart_data**: Updated chart data
    """
    try:
        chart = await chart_service.update_chart(db, chart_id, chart_data)
        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")
        return chart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{chart_id}", summary="Delete chart")
async def delete_chart(
    chart_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a chart
    
    - **chart_id**: Unique identifier of the chart to delete
    """
    try:
        success = await chart_service.delete_chart(db, chart_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chart not found")
        return {"message": "Chart deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/types/available", summary="Get available chart types")
async def get_available_chart_types():
    """
    Retrieve list of available chart types supported by the system
    """
    return {
        "chart_types": [
            {"id": "line", "name": "Line Chart", "description": "Time series and trend visualization"},
            {"id": "bar", "name": "Bar Chart", "description": "Categorical data comparison"},
            {"id": "scatter", "name": "Scatter Plot", "description": "Correlation and distribution analysis"},
            {"id": "pie", "name": "Pie Chart", "description": "Proportional data representation"},
            {"id": "histogram", "name": "Histogram", "description": "Data distribution analysis"},
            {"id": "heatmap", "name": "Heatmap", "description": "Matrix data visualization"},
            {"id": "3d_scatter", "name": "3D Scatter Plot", "description": "Three-dimensional data visualization"},
            {"id": "choropleth", "name": "Choropleth Map", "description": "Geographic data visualization"}
        ]
    }

@router.get("/sources/available", summary="Get available data sources")
async def get_available_data_sources(db: Session = Depends(get_db)):
    """
    Retrieve list of available data sources for chart creation
    """
    try:
        sources = await chart_service.get_available_data_sources(db)
        return {"data_sources": sources}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{chart_id}/export", summary="Export chart")
async def export_chart(
    chart_id: int,
    format: str = Query("png", description="Export format (png, svg, pdf, html)"),
    db: Session = Depends(get_db)
):
    """
    Export a chart in the specified format
    
    - **chart_id**: Unique identifier of the chart to export
    - **format**: Export format (png, svg, pdf, html)
    """
    try:
        export_data = await chart_service.export_chart(db, chart_id, format)
        return export_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chart_id}/preview", summary="Get chart preview")
async def get_chart_preview(
    chart_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a preview of the chart (HTML representation)
    
    - **chart_id**: Unique identifier of the chart
    """
    try:
        preview = await chart_service.get_chart_preview(db, chart_id)
        if not preview:
            raise HTTPException(status_code=404, detail="Chart not found")
        return preview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

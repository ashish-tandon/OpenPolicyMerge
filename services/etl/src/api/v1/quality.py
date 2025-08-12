"""
Data Quality API endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/", tags=["Quality"])
async def list_quality_metrics():
    """List all data quality metrics."""
    return {"metrics": [], "total": 0}

@router.get("/{metric_id}", tags=["Quality"])
async def get_quality_metric(metric_id: str):
    """Get data quality metric by ID."""
    return {"id": metric_id, "name": "example-metric"}

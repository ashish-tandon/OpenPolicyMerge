"""
Charts API endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/", tags=["Charts"])
async def list_charts():
    """List all charts."""
    return {"charts": [], "total": 0}

@router.get("/{chart_id}", tags=["Charts"])
async def get_chart(chart_id: str):
    """Get chart by ID."""
    return {"id": chart_id, "name": "example-chart"}

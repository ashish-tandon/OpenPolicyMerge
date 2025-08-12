"""
Data Sources API endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/", tags=["Sources"])
async def list_sources():
    """List all data sources."""
    return {"sources": [], "total": 0}

@router.get("/{source_id}", tags=["Sources"])
async def get_source(source_id: str):
    """Get data source by ID."""
    return {"id": source_id, "name": "example-source"}

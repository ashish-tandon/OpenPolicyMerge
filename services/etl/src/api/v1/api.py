"""
Main API router for ETL service v1.
"""
from fastapi import APIRouter

from . import jobs, sources, quality, charts

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(sources.router, prefix="/sources", tags=["Sources"])
api_router.include_router(quality.router, prefix="/quality", tags=["Quality"])
api_router.include_router(charts.router, prefix="/charts", tags=["Charts"])

# Health check endpoint
@api_router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for ETL service."""
    return {"status": "healthy", "service": "ETL Service"}

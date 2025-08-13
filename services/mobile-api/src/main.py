"""
Main entry point for Mobile API Service
"""
from fastapi import FastAPI
from .config import config
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level.upper()),
    format=config.logging.format
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=config.service.name,
    description="Mobile API Service for OpenPolicy Platform",
    version=config.service.version
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": config.service.name,
        "version": config.service.version,
        "status": "running",
        "port": config.service.port
    }

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": config.service.name,
        "version": config.service.version,
        "port": config.service.port
    }

@app.get("/health")
async def health_check_alt():
    """Alternative health check endpoint"""
    return await health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=True
    )

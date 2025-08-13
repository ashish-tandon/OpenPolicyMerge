"""
Main entry point for Error Reporting Service
"""
from fastapi import FastAPI
from .config import Config
from .api import router
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=Config.SERVICE_NAME,
    description="Error Reporting Service for OpenPolicy Platform",
    version=Config.SERVICE_VERSION
)

# Include API router
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": Config.SERVICE_NAME,
        "version": Config.SERVICE_VERSION,
        "status": "running",
        "port": Config.SERVICE_PORT
    }

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": Config.SERVICE_NAME,
        "version": Config.SERVICE_VERSION,
        "port": Config.SERVICE_PORT
    }

@app.get("/health")
async def health_check_alt():
    """Alternative health check endpoint"""
    return await health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.SERVICE_PORT,
        reload=True
    )

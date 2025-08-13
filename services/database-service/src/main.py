"""
Database Service
Provides database management and connection pooling for the OpenPolicy platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from .config import Config
from .api import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=Config.SERVICE_NAME,
    description="Database management and connection pooling service",
    version=Config.SERVICE_VERSION
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api/v1", tags=["database"])

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

@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "service": Config.SERVICE_NAME,
        "version": Config.SERVICE_VERSION,
        "port": Config.SERVICE_PORT
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.SERVICE_PORT,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )

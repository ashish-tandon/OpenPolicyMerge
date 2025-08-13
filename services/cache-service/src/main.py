"""
Cache Service
Provides Redis caching and memory management for the OpenPolicy platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cache Service",
    description="Redis caching and memory management service",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cache-service",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check_alt():
    """Alternative health check endpoint"""
    return await health_check()

@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "service": "cache-service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9016,
        reload=True,
        log_level="info"
    )

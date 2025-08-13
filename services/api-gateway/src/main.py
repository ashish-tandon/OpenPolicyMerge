"""
Main entry point for API Gateway Service
"""
from fastapi import FastAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="API Gateway",
    description="API Gateway Service for OpenPolicy Platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "status": "running",
        "port": 9001
    }

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "port": 9001
    }

@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "service": "api-gateway",
        "version": "1.0.0",
        "port": 9001
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
        port=9001,
        reload=True
    )

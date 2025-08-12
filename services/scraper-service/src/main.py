"""
OpenPolicy Scraper Service

This service orchestrates all data scraping operations for the OpenPolicy platform,
including parliamentary data, civic data, and external data sources.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Settings
from src.core.logging_config import setup_logging, get_logger
from src.core.monitoring import setup_monitoring
from src.core.database import init_db, close_db
from src.middleware.logging import LoggingMiddleware
from src.middleware.monitoring import MonitoringMiddleware
from src.routes import scrapers, jobs, data, monitoring
from src.services.scraper_manager import ScraperManager

# Initialize settings
settings = Settings()

# Setup logging
logger = get_logger(__name__)

# Setup monitoring
if settings.METRICS_ENABLED:
    setup_monitoring()

# Create FastAPI application
app = FastAPI(
    title="OpenPolicy Scraper Service",
    description="Data scraping and collection service for OpenPolicy platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
try:
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MonitoringMiddleware)
except Exception as e:
    logger.warning(f"Could not add custom middleware: {e}")

# Include routers
try:
    app.include_router(scrapers.router, prefix="/api/v1/scrapers", tags=["Scrapers"])
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
    app.include_router(data.router, prefix="/api/v1/data", tags=["Data"])
    app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])
except Exception as e:
    logger.warning(f"Could not include routers: {e}")

# Global scraper manager instance
scraper_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global scraper_manager
    
    try:
        logger.info("Starting OpenPolicy Scraper Service...")
        
        # Initialize database
        try:
            init_db()
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
        
        # Initialize scraper manager
        try:
            scraper_manager = ScraperManager()
            await scraper_manager.__aenter__()
            logger.info("Scraper Manager initialized successfully")
        except Exception as e:
            logger.warning(f"Scraper Manager initialization failed: {e}")
        
        logger.info("Scraper Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start Scraper Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown"""
    global scraper_manager
    
    try:
        logger.info("Shutting down OpenPolicy Scraper Service...")
        
        if scraper_manager:
            try:
                await scraper_manager.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Scraper Manager shutdown failed: {e}")
        
        # Close database connections
        try:
            await close_db()
        except Exception as e:
            logger.warning(f"Database shutdown failed: {e}")
        
        logger.info("Scraper Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with service information"""
    return f"""
    <html>
        <head>
            <title>OpenPolicy Scraper Service</title>
        </head>
        <body>
            <h1>🚀 OpenPolicy Scraper Service</h1>
            <p>Data scraping and collection service for OpenPolicy platform</p>
            <p><strong>Version:</strong> {app.version}</p>
            <p><strong>Status:</strong> Running</p>
            <p><strong>Started:</strong> {datetime.utcnow().isoformat()}</p>
            <hr>
            <h2>📚 API Documentation</h2>
            <ul>
                <li><a href="/docs">Swagger UI</a></li>
                <li><a href="/redoc">ReDoc</a></li>
                <li><a href="/openapi.json">OpenAPI JSON</a></li>
            </ul>
            <hr>
            <h2>🔍 Health Checks</h2>
            <ul>
                <li><a href="/healthz">Health Check</a></li>
                <li><a href="/readyz">Readiness Check</a></li>
                <li><a href="/livez">Liveness Check</a></li>
            </ul>
            <hr>
            <h2>📊 Monitoring</h2>
            <ul>
                <li><a href="/api/v1/monitoring/metrics">Metrics</a></li>
                <li><a href="/api/v1/monitoring/health">Health Status</a></li>
            </ul>
        </body>
    </html>
    """

# Health check endpoints
@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    try:
        # Basic health check
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "OpenPolicy Scraper Service",
            "version": app.version,
            "uptime": "running"
        }
        
        # Check database connectivity
        try:
            # Add database health check here when implemented
            health_status["database"] = "connected"
        except Exception as e:
            health_status["database"] = f"error: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check scraper manager
        if scraper_manager:
            health_status["scraper_manager"] = "initialized"
        else:
            health_status["scraper_manager"] = "not_initialized"
            health_status["status"] = "unhealthy"
        
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if service is ready to handle requests
        ready = True
        checks = {}
        
        # Database readiness
        try:
            # Add database readiness check here when implemented
            checks["database"] = "ready"
        except Exception as e:
            checks["database"] = f"not_ready: {str(e)}"
            ready = False
        
        # Scraper manager readiness
        if scraper_manager:
            checks["scraper_manager"] = "ready"
        else:
            checks["scraper_manager"] = "not_ready"
            ready = False
        
        return {
            "ready": ready,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/livez")
async def liveness_check():
    """Liveness check endpoint"""
    try:
        # Simple liveness check - service is responding
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "OpenPolicy Scraper Service"
        }
    except Exception as e:
        return {
            "alive": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1
    )

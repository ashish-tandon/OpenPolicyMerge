"""
OpenPolicy Scraper Service v2.0

This service orchestrates all data scraping operations for the OpenPolicy platform,
including parliamentary data, civic data, and external data sources.
Features dual database support (test/prod) and efficiency optimizations.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import sys
from datetime import datetime
import asyncio

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from src.core.logging_config import setup_logging, get_logger
from src.core.monitoring import setup_monitoring
from src.core.database import init_db, close_db
from src.middleware.logging import LoggingMiddleware
from src.middleware.monitoring import MonitoringMiddleware
from src.routes import scrapers, jobs, data, monitoring
from src.services.scraper_manager import ScraperManager

# Setup logging
logger = get_logger(__name__)

# Setup monitoring
if config.METRICS_ENABLED:
    setup_monitoring()

# Create FastAPI application
app = FastAPI(
    title="OpenPolicy Scraper Service v2.0",
    description="Data scraping and collection service for OpenPolicy platform with dual DB support",
    version="2.0.0",
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
    """Initialize services on startup with efficiency optimizations"""
    global scraper_manager
    
    try:
        logger.info(f"Starting OpenPolicy Scraper Service v2.0 in {config.mode.upper()} mode...")
        logger.info(f"Database: {config.DATABASE_NAME}")
        logger.info(f"Optimizations: Connection Pooling={config.ENABLE_CONNECTION_POOLING}, "
                   f"Query Caching={config.ENABLE_QUERY_CACHING}, "
                   f"Batch Processing={config.ENABLE_BATCH_PROCESSING}, "
                   f"Async Processing={config.ENABLE_ASYNC_PROCESSING}")
        
        # Initialize database with connection pooling
        try:
            if config.ENABLE_CONNECTION_POOLING:
                logger.info("Initializing database with connection pooling...")
            init_db()
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
        
        # Initialize scraper manager with efficiency optimizations
        try:
            scraper_manager = ScraperManager()
            await scraper_manager.__aenter__()
            logger.info("Scraper Manager initialized successfully with optimizations")
        except Exception as e:
            logger.warning(f"Scraper Manager initialization failed: {e}")
        
        logger.info("Scraper Service v2.0 started successfully")
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
                logger.warning(f"Scraper Manager cleanup failed: {e}")
        
        # Close database connections
        try:
            close_db()
        except Exception as e:
            logger.warning(f"Database cleanup failed: {e}")
        
        logger.info("Scraper Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Health check endpoints
@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "scraper-service",
        "version": "2.0.0",
        "mode": config.mode,
        "database": config.DATABASE_NAME,
        "timestamp": datetime.utcnow().isoformat(),
        "optimizations": {
            "connection_pooling": config.ENABLE_CONNECTION_POOLING,
            "query_caching": config.ENABLE_QUERY_CACHING,
            "batch_processing": config.ENABLE_BATCH_PROCESSING,
            "async_processing": config.ENABLE_ASYNC_PROCESSING
        }
    }

@app.get("/readyz", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if scraper manager is ready
        if scraper_manager and hasattr(scraper_manager, 'is_ready'):
            ready = await scraper_manager.is_ready()
        else:
            ready = scraper_manager is not None
        
        return {
            "status": "ready" if ready else "not_ready",
            "service": "scraper-service",
            "mode": config.mode,
            "database": config.DATABASE_NAME,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Mode information endpoint
@app.get("/mode", tags=["Configuration"])
async def get_mode_info():
    """Get current service mode and configuration"""
    return config.get_mode_info()

# Performance metrics endpoint
@app.get("/performance", tags=["Monitoring"])
async def get_performance_metrics():
    """Get performance optimization metrics"""
    return {
        "concurrent_scrapers": config.MAX_CONCURRENT_SCRAPERS,
        "batch_size": config.BATCH_SIZE,
        "cache_ttl": config.CACHE_TTL,
        "rate_limit": config.RATE_LIMIT_PER_MINUTE,
        "timeouts": {
            "scraper": config.SCRAPER_TIMEOUT,
            "processing": config.PROCESSING_TIMEOUT,
            "default": config.DEFAULT_TIMEOUT
        },
        "retry_config": {
            "attempts": config.RETRY_ATTEMPTS,
            "delay": config.SCRAPER_RETRY_DELAY
        }
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenPolicy Scraper Service v2.0</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 20px; border-radius: 10px; }}
            .info {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .mode {{ font-weight: bold; color: #28a745; }}
            .optimization {{ background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 OpenPolicy Scraper Service v2.0</h1>
            <p>High-performance data scraping with dual database support</p>
        </div>
        
        <div class="info">
            <h2>Service Status</h2>
            <p><strong>Mode:</strong> <span class="mode">{config.mode.upper()}</span></p>
            <p><strong>Database:</strong> {config.DATABASE_NAME}</p>
            <p><strong>Version:</strong> {config.APP_VERSION}</p>
        </div>
        
        <div class="info">
            <h2>Efficiency Optimizations</h2>
            <div class="optimization">🔗 Connection Pooling: {config.ENABLE_CONNECTION_POOLING}</div>
            <div class="optimization">💾 Query Caching: {config.ENABLE_QUERY_CACHING}</div>
            <div class="optimization">📦 Batch Processing: {config.ENABLE_BATCH_PROCESSING}</div>
            <div class="optimization">⚡ Async Processing: {config.ENABLE_ASYNC_PROCESSING}</div>
        </div>
        
        <div class="info">
            <h2>Performance Metrics</h2>
            <p><strong>Max Concurrent Scrapers:</strong> {config.MAX_CONCURRENT_SCRAPERS}</p>
            <p><strong>Batch Size:</strong> {config.BATCH_SIZE}</p>
            <p><strong>Rate Limit:</strong> {config.RATE_LIMIT_PER_MINUTE} requests/minute</p>
        </div>
        
        <div class="info">
            <h2>API Endpoints</h2>
            <p><a href="/docs">📚 API Documentation</a></p>
            <p><a href="/healthz">❤️ Health Check</a></p>
            <p><a href="/readyz">✅ Readiness Check</a></p>
            <p><a href="/mode">⚙️ Mode Information</a></p>
            <p><a href="/performance">📊 Performance Metrics</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with logging"""
    logger.error(f"Global exception handler: {exc} for request {request.url}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
            "mode": config.mode
        }
    )

if __name__ == "__main__":
    # Run with uvicorn for development
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )

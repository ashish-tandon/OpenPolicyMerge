"""
OpenPolicy Health Service

This service provides comprehensive health monitoring for all OpenPolicy platform services,
including health checks, dependency monitoring, and alert generation.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import sys
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from core.logging import setup_logging
from core.monitoring import setup_monitoring
from database import init_db, close_db
from middleware.logging import LoggingMiddleware
from middleware.monitoring import MonitoringMiddleware
from routes import health, services, alerts, metrics
from services.health_monitor import HealthMonitor

# Setup logging
setup_logging()
logger = setup_logging()

# Setup monitoring
if settings.monitoring.enabled:
    setup_monitoring()

# Create FastAPI application
app = FastAPI(
    title="OpenPolicy Health Service",
    description="Comprehensive health monitoring service for OpenPolicy platform",
    version="1.0.0",
    docs_url="/docs" if settings.swagger.enabled else None,
    redoc_url="/redoc" if settings.swagger.enabled else None,
    openapi_url="/openapi.json" if settings.swagger.enabled else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(MonitoringMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])

# Global health monitor instance
health_monitor = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global health_monitor
    
    try:
        logger.info("Starting OpenPolicy Health Service...")
        
        # Initialize database
        await init_db()
        
        # Initialize health monitor
        health_monitor = HealthMonitor()
        await health_monitor.initialize()
        
        # Start health monitoring
        await health_monitor.start_monitoring()
        
        logger.info("Health Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start Health Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown"""
    global health_monitor
    
    try:
        logger.info("Shutting down OpenPolicy Health Service...")
        
        if health_monitor:
            await health_monitor.stop_monitoring()
        
        await close_db()
        logger.info("Health Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with service information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenPolicy Health Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .endpoints { background: #fff; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; }
            .endpoint { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }
            .method { font-weight: bold; color: #007bff; }
            .url { font-family: monospace; color: #28a745; }
            .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .healthy { background: #d4edda; color: #155724; }
            .unhealthy { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 OpenPolicy Health Service</h1>
                <p>Comprehensive health monitoring service for the OpenPolicy platform</p>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Status:</strong> <span class="status healthy">🟢 Operational</span></p>
            </div>
            
            <div class="endpoints">
                <h2>📊 Available Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/health</span>
                    <span> - Overall platform health status</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/services</span>
                    <span> - Individual service health status</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/alerts</span>
                    <span> - Active alerts and notifications</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/metrics</span>
                    <span> - Health metrics and statistics</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/healthz</span>
                    <span> - Health check endpoint</span>
                </div>
            </div>
            
            <div class="endpoints">
                <h2>🔧 Features</h2>
                <ul>
                    <li>🏥 Service health monitoring</li>
                    <li>🔍 Dependency health checks</li>
                    <li>📊 Health status aggregation</li>
                    <li>🚨 Alert generation</li>
                    <li>🔄 Service recovery coordination</li>
                    <li>📈 Health metrics collection</li>
                    <li>🌐 Multi-service health dashboard</li>
                    <li>⚡ Real-time health updates</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "health-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "0s"  # TODO: Calculate actual uptime
    }

@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check database connection
        from database import check_db_connection
        db_healthy = await check_db_connection()
        
        if db_healthy:
            return {
                "status": "ready",
                "service": "health-service",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "service": "health-service",
                    "database": "disconnected",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "health-service",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/livez")
async def liveness_check():
    """Liveness check endpoint"""
    return {
        "status": "alive",
        "service": "health-service",
        "timestamp": datetime.utcnow().isoformat()
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.debug,
        log_level=settings.logging.level.lower()
    )

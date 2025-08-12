"""
OpenPolicy Plotly Data Visualization Service

This service provides interactive data visualization capabilities using Plotly,
including charts, dashboards, and data analysis tools for the OpenPolicy platform.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from core.logging import setup_logging
from core.monitoring import setup_monitoring
from database import init_db, close_db
from middleware.logging import LoggingMiddleware
from middleware.monitoring import MonitoringMiddleware
from middleware.rate_limit import RateLimitMiddleware
from routes import charts, dashboards, analytics, exports, templates

# Setup logging
setup_logging()
logger = setup_logging()

# Setup monitoring
if settings.monitoring.enabled:
    setup_monitoring()

# Create FastAPI application
app = FastAPI(
    title="OpenPolicy Plotly Service",
    description="Interactive data visualization service for OpenPolicy platform",
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
app.add_middleware(RateLimitMiddleware)

# Mount static files for chart exports and templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(charts.router, prefix="/api/v1/charts", tags=["Charts"])
app.include_router(dashboards.router, prefix="/api/v1/dashboards", tags=["Dashboards"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(exports.router, prefix="/api/v1/exports", tags=["Exports"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["Templates"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Starting OpenPolicy Plotly Service...")
        await init_db()
        logger.info("Plotly Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start Plotly Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown"""
    try:
        logger.info("Shutting down OpenPolicy Plotly Service...")
        await close_db()
        logger.info("Plotly Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with service information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenPolicy Plotly Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .endpoints { background: #fff; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; }
            .endpoint { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }
            .method { font-weight: bold; color: #007bff; }
            .url { font-family: monospace; color: #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 OpenPolicy Plotly Service</h1>
                <p>Interactive data visualization service for the OpenPolicy platform</p>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Status:</strong> 🟢 Operational</p>
            </div>
            
            <div class="endpoints">
                <h2>📊 Available Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/charts</span>
                    <span> - Chart management and creation</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/dashboards</span>
                    <span> - Interactive dashboard management</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/analytics</span>
                    <span> - Data analysis and insights</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/exports</span>
                    <span> - Chart and dashboard exports</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/templates</span>
                    <span> - Pre-built visualization templates</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/docs</span>
                    <span> - Interactive API documentation</span>
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
                    <li>📈 Interactive charts and graphs</li>
                    <li>📊 Real-time dashboards</li>
                    <li>🔍 Advanced data analytics</li>
                    <li>📱 Responsive visualizations</li>
                    <li>💾 Multiple export formats</li>
                    <li>🎨 Customizable themes</li>
                    <li>🌍 Geographic visualizations</li>
                    <li>📊 Statistical analysis tools</li>
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
        "service": "plotly-service",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
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
                "service": "plotly-service",
                "database": "connected",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "service": "plotly-service",
                    "database": "disconnected",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "plotly-service",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )

@app.get("/livez")
async def liveness_check():
    """Liveness check endpoint"""
    return {
        "status": "alive",
        "service": "plotly-service",
        "timestamp": "2024-01-01T00:00:00Z"
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
            "timestamp": "2024-01-01T00:00:00Z"
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

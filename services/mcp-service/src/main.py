"""
OpenPolicy MCP Service (Model Context Protocol)

This service acts as the middle layer between scrapers and databases,
processing scraped data and injecting it into the appropriate databases.
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

from config import settings
from core.logging import setup_logging
from core.monitoring import setup_monitoring
from database import init_db, close_db
from middleware.logging import LoggingMiddleware
from middleware.monitoring import MonitoringMiddleware
from routes import data_processing, data_sources, opa_integration, monitoring
from services.mcp_processor import MCPProcessor

# Setup logging
setup_logging()
logger = setup_logging()

# Setup monitoring
if settings.monitoring.enabled:
    setup_monitoring()

# Create FastAPI application
app = FastAPI(
    title="OpenPolicy MCP Service",
    description="Model Context Protocol service for data processing and database injection",
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
app.include_router(data_processing.router, prefix="/api/v1/processing", tags=["Data Processing"])
app.include_router(data_sources.router, prefix="/api/v1/sources", tags=["Data Sources"])
app.include_router(opa_integration.router, prefix="/api/v1/opa", tags=["OPA Integration"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])

# Global MCP processor instance
mcp_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global mcp_processor
    
    try:
        logger.info("Starting OpenPolicy MCP Service...")
        
        # Initialize database
        await init_db()
        
        # Initialize MCP processor
        mcp_processor = MCPProcessor()
        await mcp_processor.initialize()
        
        # Start data processing monitoring
        await mcp_processor.start_monitoring()
        
        logger.info("MCP Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start MCP Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown"""
    global mcp_processor
    
    try:
        logger.info("Shutting down OpenPolicy MCP Service...")
        
        if mcp_processor:
            await mcp_processor.stop_monitoring()
        
        await close_db()
        logger.info("MCP Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with service information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenPolicy MCP Service</title>
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
                <h1>🔗 OpenPolicy MCP Service</h1>
                <p>Model Context Protocol service for data processing and database injection</p>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Status:</strong> <span class="status healthy">🟢 Operational</span></p>
            </div>
            
            <div class="endpoints">
                <h2>📊 Available Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method">POST</span>
                    <span class="url">/api/v1/processing/ingest</span>
                    <span> - Ingest scraped data</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span>
                    <span class="url">/api/v1/processing/transform</span>
                    <span> - Transform data</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span>
                    <span class="url">/api/v1/processing/validate</span>
                    <span> - Validate data</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span>
                    <span class="url">/api/v1/processing/inject</span>
                    <span> - Inject data into database</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/sources</span>
                    <span> - Data source management</span>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/api/v1/opa/policies</span>
                    <span> - OPA policy management</span>
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
                    <li>🔗 Data pipeline orchestration</li>
                    <li>📊 Data transformation and validation</li>
                    <li>🏛️ Federal/Provincial/Municipal data processing</li>
                    <li>🔍 OPA policy integration</li>
                    <li>💾 Database injection and management</li>
                    <li>📈 Data quality monitoring</li>
                    <li>🔄 Batch processing</li>
                    <li>🚨 Error handling and recovery</li>
                </ul>
            </div>
            
            <div class="endpoints">
                <h2>📋 Supported Data Sources</h2>
                <ul>
                    <li><strong>Federal:</strong> Parliament of Canada</li>
                    <li><strong>Provincial:</strong> All 13 provinces and territories</li>
                    <li><strong>Municipal:</strong> Major cities (Toronto, Vancouver, Montreal, etc.)</li>
                    <li><strong>OpenParliament:</strong> Parliamentary data</li>
                    <li><strong>OpenNorth:</strong> Representative and boundary data</li>
                </ul>
            </div>
            
            <div class="endpoints">
                <h2>🗄️ Database Architecture</h2>
                <ul>
                    <li><strong>Single Database:</strong> openpolicy</li>
                    <li><strong>Schemas:</strong> federal, provincial, municipal, representatives, bills, etl, monitoring, auth</li>
                    <li><strong>Benefits:</strong> Easy joins, simple backup, better performance</li>
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
        "service": "mcp-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "data_sources": len(settings.data_sources.sources),
        "opa_enabled": settings.opa.enabled,
        "database_schemas": len(settings.database.schemas)
    }

@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check database connection
        from database import check_db_connection
        db_healthy = await check_db_connection()
        
        # Check OPA connection
        opa_healthy = False
        if settings.opa.enabled:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{settings.opa.url}/health", timeout=5)
                    opa_healthy = response.status_code == 200
            except Exception as e:
                logger.warning(f"OPA health check failed: {e}")
        
        if db_healthy:
            return {
                "status": "ready",
                "service": "mcp-service",
                "database": "connected",
                "opa": "connected" if opa_healthy else "disconnected",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "service": "mcp-service",
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
                "service": "mcp-service",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/livez")
async def liveness_check():
    """Liveness check endpoint"""
    return {
        "status": "alive",
        "service": "mcp-service",
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

"""
Main FastAPI application for the OpenPolicy ETL service.
"""
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_settings, settings
from database import init_db, close_db
from middleware.logging import LoggingMiddleware
from middleware.monitoring import MonitoringMiddleware
from middleware.rate_limit import RateLimitMiddleware
from api.v1.api import api_router
from core.logging import setup_logging
from core.monitoring import setup_monitoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    setup_monitoring()
    await init_db()
    
    yield
    
    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.api.title,
        description=settings.api.description,
        version=settings.api.version,
        debug=settings.api.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.api.debug else None,
        redoc_url="/redoc" if settings.api.debug else None,
        openapi_url="/openapi.json" if settings.api.debug else None
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=settings.api.cors_allow_credentials,
        allow_methods=settings.api.cors_allow_methods,
        allow_headers=settings.api.cors_allow_headers,
    )
    
    if settings.security.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware)
    
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MonitoringMiddleware)
    
    # Add trusted host middleware for production
    if settings.is_production:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    
    # Include API router
    app.include_router(api_router, prefix=f"/api/etl/v{settings.api.version.replace('.', '')}")
    
    # Global exception handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "error_code": exc.status_code,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation exceptions."""
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Validation error",
                "errors": exc.errors(),
                "path": request.url.path
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        error_message = str(exc) if settings.api.debug else "Internal server error"
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": error_message,
                "path": request.url.path
            }
        )
    
    # Health check endpoints
    @app.get("/healthz")
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "service": "openpolicy-etl",
            "version": settings.api.version,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    @app.get("/healthz/detailed")
    async def detailed_health_check():
        """Detailed health check endpoint."""
        # TODO: Add actual health checks for database, Redis, etc.
        return {
            "status": "healthy",
            "service": "openpolicy-etl",
            "version": settings.api.version,
            "timestamp": "2024-01-01T00:00:00Z",
            "components": {
                "database": "healthy",
                "redis": "healthy",
                "celery": "healthy"
            }
        }
    
    @app.get("/readyz")
    async def readiness_probe():
        """Kubernetes readiness probe."""
        # TODO: Check if service is ready to receive traffic
        return {"status": "ready"}
    
    @app.get("/livez")
    async def liveness_probe():
        """Kubernetes liveness probe."""
        # TODO: Check if service is alive
        return {"status": "alive"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "service": "OpenPolicy ETL Service",
            "version": settings.api.version,
            "description": settings.api.description,
            "status": "running",
            "docs": "/docs" if settings.api.debug else None,
            "health": "/healthz"
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level=settings.logging.level.lower()
    )

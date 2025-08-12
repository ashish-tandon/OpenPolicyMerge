"""
Monitoring middleware for the ETL service.
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.monitoring import record_request, get_health_metrics
from core.logging import get_logger


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring and observability."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.monitoring")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()
        
        # Add monitoring headers
        request.state.monitoring_start = start_time
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            record_request(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                duration=duration
            )
            
            # Add monitoring headers to response
            response.headers["X-Request-Duration"] = str(duration)
            response.headers["X-Request-ID"] = getattr(request.state, "request_id", "unknown")
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics for failed request
            record_request(
                method=request.method,
                endpoint=request.url.path,
                status=500,
                duration=duration
            )
            
            # Log monitoring error
            self.logger.error(
                f"Monitoring error for {request.method} {request.url.path}",
                extra={
                    "error": str(e),
                    "duration": duration,
                    "request_id": getattr(request.state, "request_id", "unknown")
                }
            )
            
            raise


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware for health check endpoints."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.health")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if this is a health check endpoint
        if request.url.path in ["/healthz", "/healthz/detailed", "/readyz", "/livez"]:
            # Add health check headers
            request.state.is_health_check = True
            
            # Record health check metrics
            start_time = time.time()
            
            try:
                response = await call_next(request)
                duration = time.time() - start_time
                
                # Add health check timing header
                response.headers["X-Health-Check-Duration"] = str(duration)
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                
                self.logger.error(
                    f"Health check failed: {request.url.path}",
                    extra={
                        "error": str(e),
                        "duration": duration,
                        "endpoint": request.url.path
                    }
                )
                
                raise
        
        # For non-health check endpoints, proceed normally
        return await call_next(request)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for metrics collection."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.metrics")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if this is a metrics endpoint
        if request.url.path == "/metrics":
            # Add metrics headers
            request.state.is_metrics_request = True
            
            try:
                response = await call_next(request)
                
                # Add metrics response headers
                response.headers["X-Metrics-Timestamp"] = str(int(time.time()))
                
                return response
                
            except Exception as e:
                self.logger.error(
                    "Metrics endpoint failed",
                    extra={
                        "error": str(e),
                        "endpoint": "/metrics"
                    }
                )
                
                raise
        
        # For non-metrics endpoints, proceed normally
        return await call_next(request)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.performance")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start performance monitoring
        start_time = time.time()
        
        # Add performance context
        request.state.performance_start = start_time
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate performance metrics
            duration = time.time() - start_time
            
            # Log slow requests
            if duration > 1.0:  # Log requests taking more than 1 second
                self.logger.warning(
                    f"Slow request detected: {request.method} {request.url.path}",
                    extra={
                        "duration": duration,
                        "method": request.method,
                        "path": request.url.path,
                        "request_id": getattr(request.state, "request_id", "unknown")
                    }
                )
            
            # Add performance headers
            response.headers["X-Response-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            # Calculate duration even for failed requests
            duration = time.time() - start_time
            
            # Log performance error
            self.logger.error(
                f"Performance monitoring error: {request.method} {request.url.path}",
                extra={
                    "error": str(e),
                    "duration": duration,
                    "request_id": getattr(request.state, "request_id", "unknown")
                }
            )
            
            raise


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security monitoring."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.security")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Security checks
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        # Log suspicious requests
        if self._is_suspicious_request(request, client_ip, user_agent):
            self.logger.warning(
                f"Suspicious request detected: {request.method} {request.url.path}",
                extra={
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "method": request.method,
                    "path": request.url.path,
                    "request_id": getattr(request.state, "request_id", "unknown")
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
    
    def _is_suspicious_request(self, request: Request, client_ip: str, user_agent: str) -> bool:
        """Check if request is suspicious."""
        # Check for common attack patterns
        suspicious_patterns = [
            "/admin", "/wp-admin", "/phpmyadmin", "/config",
            "union select", "script>", "javascript:", "eval(",
            "document.cookie", "alert(", "onload="
        ]
        
        # Check path
        path = request.url.path.lower()
        if any(pattern in path for pattern in suspicious_patterns):
            return True
        
        # Check query parameters
        query = str(request.query_params).lower()
        if any(pattern in query for pattern in suspicious_patterns):
            return True
        
        # Check for suspicious user agents
        suspicious_user_agents = [
            "sqlmap", "nikto", "nmap", "wget", "curl",
            "python-requests", "scanner", "bot"
        ]
        
        if any(agent in user_agent.lower() for agent in suspicious_user_agents):
            return True
        
        return False

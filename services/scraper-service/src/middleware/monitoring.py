"""
Monitoring middleware for OpenPolicy Scraper Service
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.monitoring import record_scraper_request, record_scraper_duration

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring HTTP requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Start time
        start_time = time.time()
        
        # Extract scraper name from path if available
        scraper_name = "unknown"
        if request.url.path.startswith("/api/v1/scrapers/"):
            path_parts = request.url.path.split("/")
            if len(path_parts) > 4:
                scraper_name = path_parts[4]
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            record_scraper_request(scraper_name, "success")
            record_scraper_duration(scraper_name, duration)
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record error metrics
            record_scraper_request(scraper_name, "error")
            record_scraper_duration(scraper_name, duration)
            
            # Re-raise exception
            raise

"""
Standardized Service Integration for Error Reporting
All services should import and use this module
"""
import httpx
import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

class ServiceErrorReporter:
    """Standardized error reporting for all OpenPolicy services"""
    
    def __init__(self, service_name: str, service_port: int, error_service_url: str = "http://localhost:9024"):
        self.service_name = service_name
        self.service_port = service_port
        self.error_service_url = error_service_url
        self.logger = logging.getLogger(f"{service_name}.error_reporter")
        
    async def report_error(self, 
                          error: Exception, 
                          context: Dict[str, Any] = None,
                          severity: str = "ERROR",
                          user_id: Optional[str] = None) -> bool:
        """Report an error to the centralized error reporting service"""
        try:
            error_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "service_name": self.service_name,
                "service_port": self.service_port,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_traceback": traceback.format_exc(),
                "severity": severity.upper(),
                "context": context or {},
                "user_id": user_id,
                "host": "localhost",
                "environment": "development"
            }
            
            # Send to error reporting service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.error_service_url}/api/errors/report",
                    json=error_data,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    self.logger.info(f"Error reported successfully: {error_data['error_type']}")
                    return True
                else:
                    self.logger.warning(f"Failed to report error: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to report error to error service: {e}")
            return False
    
    async def report_log(self, 
                        level: str, 
                        message: str, 
                        context: Dict[str, Any] = None) -> bool:
        """Report a log entry to the centralized service"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "service_name": self.service_name,
                "service_port": self.service_port,
                "log_level": level.upper(),
                "message": message,
                "context": context or {},
                "host": "localhost",
                "environment": "development"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.error_service_url}/api/errors/log",
                    json=log_data,
                    timeout=5.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Failed to report log: {e}")
            return False
    
    async def check_health(self) -> Dict[str, Any]:
        """Check error reporting service health"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.error_service_url}/healthz",
                    timeout=5.0
                )
                
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "last_check": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "disconnected",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }

def error_reporting_decorator(service_name: str, service_port: int):
    """Decorator to automatically report errors to centralized service"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Report error to centralized service
                reporter = ServiceErrorReporter(service_name, service_port)
                await reporter.report_error(e, {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                raise e
        return wrapper
    return decorator

# Global error reporter instances for common services
policy_service_reporter = ServiceErrorReporter("policy-service", 9001)
search_service_reporter = ServiceErrorReporter("search-service", 9002)
notification_service_reporter = ServiceErrorReporter("notification-service", 9004)
config_service_reporter = ServiceErrorReporter("config-service", 9005)
scraper_service_reporter = ServiceErrorReporter("scraper-service", 9008)
monitoring_service_reporter = ServiceErrorReporter("monitoring-service", 9010)

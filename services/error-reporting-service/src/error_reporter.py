"""
Standardized Error Reporter Module
All services must use this module for error reporting
"""
import httpx
import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from .config import Config

class ErrorReporter:
    """Centralized error reporting for all services"""
    
    def __init__(self, service_name: str, service_port: int, error_service_url: str = None):
        self.service_name = service_name
        self.service_port = service_port
        self.error_service_url = error_service_url or Config.ERROR_REPORTING_URL
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
                "host": Config.SERVICE_HOST,
                "environment": Config.ENVIRONMENT
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
                "host": Config.SERVICE_HOST,
                "environment": Config.ENVIRONMENT
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

# Global error reporter instance
error_reporter = ErrorReporter(
    service_name=Config.SERVICE_NAME,
    service_port=Config.SERVICE_PORT
)

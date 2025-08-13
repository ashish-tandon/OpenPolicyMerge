"""
Configuration for API Gateway Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "api-gateway"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9001))
    
    # Gateway configuration
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    
    # External service dependencies
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:9003")
    POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:9001")
    SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:9002")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

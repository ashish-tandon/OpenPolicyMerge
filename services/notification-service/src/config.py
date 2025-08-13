"""
Configuration for Notification Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "notification-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9004))
    
    # Notification configuration
    ENABLE_EMAIL = os.getenv("ENABLE_EMAIL", "true").lower() == "true"
    ENABLE_SMS = os.getenv("ENABLE_SMS", "false").lower() == "true"
    ENABLE_PUSH = os.getenv("ENABLE_PUSH", "true").lower() == "true"
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    ERROR_REPORTING_URL = os.getenv("ERROR_REPORTING_URL", "http://localhost:9024")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Performance settings
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    MAX_MEMORY_USAGE = int(os.getenv("MAX_MEMORY_USAGE", 1024 * 1024 * 1024))  # 1GB
    
    # Security settings
    ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    # Monitoring
    ENABLE_SLOW_REQUEST_LOGGING = os.getenv("ENABLE_SLOW_REQUEST_LOGGING", "true").lower() == "true"
    SLOW_REQUEST_THRESHOLD = float(os.getenv("SLOW_REQUEST_THRESHOLD", 2.0))  # 2 seconds

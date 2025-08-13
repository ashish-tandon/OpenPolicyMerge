"""
Configuration for Error Reporting Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "error-reporting-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9024))
    SERVICE_HOST = os.getenv("SERVICE_HOST", "localhost")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Error reporting configuration
    ENABLE_REAL_TIME_MONITORING = os.getenv("ENABLE_REAL_TIME_MONITORING", "true").lower() == "true"
    ERROR_RETENTION_DAYS = int(os.getenv("ERROR_RETENTION_DAYS", 90))
    ENABLE_ERROR_AGGREGATION = os.getenv("ENABLE_ERROR_AGGREGATION", "true").lower() == "true"
    
    # Alert configuration
    ENABLE_ALERTS = os.getenv("ENABLE_ALERTS", "true").lower() == "true"
    ALERT_CHANNELS = os.getenv("ALERT_CHANNELS", "email,slack,webhook").split(",")
    CRITICAL_ERROR_THRESHOLD = int(os.getenv("CRITICAL_ERROR_THRESHOLD", 10))
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 10))
    
    # Cache configuration
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    MONITORING_SERVICE_URL = os.getenv("MONITORING_SERVICE_URL", "http://localhost:9010")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:9004")
    
    # Health check
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
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

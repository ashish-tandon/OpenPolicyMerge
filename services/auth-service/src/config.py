"""
Configuration for Auth Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "auth-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9003))
    
    # Authentication configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
    JWT_EXPIRES_IN = os.getenv("JWT_EXPIRES_IN", "24h")
    JWT_REFRESH_EXPIRES_IN = os.getenv("JWT_REFRESH_EXPIRES_IN", "7d")
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))
    
    # Security settings
    ENABLE_2FA = os.getenv("ENABLE_2FA", "true").lower() == "true"
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 3600))
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:9001")
    SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:9002")
    
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

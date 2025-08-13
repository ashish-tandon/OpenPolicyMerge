"""
Configuration for Mobile API Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "mobile-api"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9020))
    
    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))
    
    # Cache configuration
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))
    
    # Authentication
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_EXPIRES_IN = os.getenv("JWT_EXPIRES_IN", "24h")
    JWT_REFRESH_EXPIRES_IN = os.getenv("JWT_REFRESH_EXPIRES_IN", "7d")
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:9003")
    POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:9001")
    SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:9002")
    ETL_SERVICE_URL = os.getenv("ETL_SERVICE_URL", "http://localhost:9007")
    
    # Mobile-specific features
    ENABLE_PUSH_NOTIFICATIONS = os.getenv("ENABLE_PUSH_NOTIFICATIONS", "true").lower() == "true"
    ENABLE_OFFLINE_MODE = os.getenv("ENABLE_OFFLINE_MODE", "true").lower() == "true"
    MAX_OFFLINE_DATA = int(os.getenv("MAX_OFFLINE_DATA", 100 * 1024 * 1024))
    SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", 300000))
    
    # API rate limiting
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    RATE_LIMIT_WINDOW_MS = int(os.getenv("RATE_LIMIT_WINDOW_MS", 15 * 60 * 1000))
    RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", 100))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30000))
    HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", 5000))
    
    # Performance
    ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    MAX_PAYLOAD_SIZE = int(os.getenv("MAX_PAYLOAD_SIZE", 10 * 1024 * 1024))
    
    # Security
    ENABLE_HELMET = os.getenv("ENABLE_HELMET", "true").lower() == "true"
    ENABLE_HSTS = os.getenv("ENABLE_HSTS", "true").lower() == "true"
    ENABLE_XSS_PROTECTION = os.getenv("ENABLE_XSS_PROTECTION", "true").lower() == "true"
    
    # Monitoring
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    ENABLE_PROFILING = os.getenv("ENABLE_PROFILING", "true").lower() == "true"
    
    # Development
    NODE_ENV = os.getenv("NODE_ENV", "development")

# Create config instance
config = Config()

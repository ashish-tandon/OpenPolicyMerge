"""
Configuration for Cache Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "cache-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9016))
    
    # Redis configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Cache configuration
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 hour default
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 1000))
    CACHE_EVICTION_POLICY = os.getenv("CACHE_EVICTION_POLICY", "lru")
    
    # External service dependencies
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    QUEUE_URL = os.getenv("QUEUE_URL", "amqp://localhost:5672")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Metrics collection
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Performance settings
    CONNECTION_POOL_SIZE = int(os.getenv("CONNECTION_POOL_SIZE", 10))
    CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", 30))
    CONNECTION_RETRY_ATTEMPTS = int(os.getenv("CONNECTION_RETRY_ATTEMPTS", 3))
    
    # Cache policies
    ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
    COMPRESSION_THRESHOLD = int(os.getenv("COMPRESSION_THRESHOLD", 1024))  # 1KB
    ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "false").lower() == "true"
    
    # Monitoring
    ENABLE_SLOW_QUERY_LOGGING = os.getenv("ENABLE_SLOW_QUERY_LOGGING", "true").lower() == "true"
    SLOW_QUERY_THRESHOLD = float(os.getenv("SLOW_QUERY_THRESHOLD", 0.1))  # 100ms

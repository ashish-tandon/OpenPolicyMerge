"""
Configuration for Database Service
"""

import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "database-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9015))
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 10))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", 20))
    
    # External service dependencies
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    QUEUE_URL = os.getenv("QUEUE_URL", "amqp://localhost:5672")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Metrics collection
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Connection pooling
    CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", 30))
    CONNECTION_RETRY_ATTEMPTS = int(os.getenv("CONNECTION_RETRY_ATTEMPTS", 3))
    
    # Performance settings
    QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT", 60))
    MAX_CONCURRENT_QUERIES = int(os.getenv("MAX_CONCURRENT_QUERIES", 100))

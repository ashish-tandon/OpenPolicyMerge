"""
Configuration for OP Import Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "op-import"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9023))
    
    # Import configuration
    IMPORT_BATCH_SIZE = int(os.getenv("IMPORT_BATCH_SIZE", 1000))
    IMPORT_MAX_WORKERS = int(os.getenv("IMPORT_MAX_WORKERS", 4))
    IMPORT_TIMEOUT = int(os.getenv("IMPORT_TIMEOUT", 300))  # 5 minutes
    IMPORT_RETRY_ATTEMPTS = int(os.getenv("IMPORT_RETRY_ATTEMPTS", 3))
    
    # Data source configuration
    DATA_SOURCES = os.getenv("DATA_SOURCES", "openparliament,opennorth").split(",")
    ENABLE_REAL_TIME_IMPORT = os.getenv("ENABLE_REAL_TIME_IMPORT", "true").lower() == "true"
    IMPORT_INTERVAL = int(os.getenv("IMPORT_INTERVAL", 3600))  # 1 hour
    
    # Data validation
    ENABLE_DATA_VALIDATION = os.getenv("ENABLE_DATA_VALIDATION", "true").lower() == "true"
    STRICT_VALIDATION = os.getenv("STRICT_VALIDATION", "false").lower() == "true"
    MIN_QUALITY_SCORE = float(os.getenv("MIN_QUALITY_SCORE", 0.8))
    
    # Data transformation
    ENABLE_DATA_TRANSFORMATION = os.getenv("ENABLE_DATA_TRANSFORMATION", "true").lower() == "true"
    ENABLE_DATA_NORMALIZATION = os.getenv("ENABLE_DATA_NORMALIZATION", "true").lower() == "true"
    ENABLE_DUPLICATE_DETECTION = os.getenv("ENABLE_DUPLICATE_DETECTION", "true").lower() == "true"
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 10))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", 20))
    
    # Cache configuration
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 hour
    
    # Queue configuration
    QUEUE_URL = os.getenv("QUEUE_URL", "amqp://localhost:5672")
    QUEUE_NAME = os.getenv("QUEUE_NAME", "op_import_queue")
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    ETL_SERVICE_URL = os.getenv("ETL_SERVICE_URL", "http://localhost:9007")
    POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:9001")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.getenv("LOG_FILE", "/app/logs/op_import.log")
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Performance settings
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_PROFILING = os.getenv("ENABLE_PROFILING", "false").lower() == "true"
    
    # Monitoring
    ENABLE_SLOW_IMPORT_LOGGING = os.getenv("ENABLE_SLOW_IMPORT_LOGGING", "true").lower() == "true"
    SLOW_IMPORT_THRESHOLD = float(os.getenv("SLOW_IMPORT_THRESHOLD", 10.0))  # 10 seconds
    
    # Error handling
    ENABLE_ERROR_RECOVERY = os.getenv("ENABLE_ERROR_RECOVERY", "true").lower() == "true"
    MAX_ERROR_COUNT = int(os.getenv("MAX_ERROR_COUNT", 100))
    ERROR_NOTIFICATION_ENABLED = os.getenv("ERROR_NOTIFICATION_ENABLED", "true").lower() == "true"

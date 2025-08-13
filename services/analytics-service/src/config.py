"""
Configuration for Analytics Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "analytics-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9013))
    
    # Analytics configuration
    ENABLE_REAL_TIME_ANALYTICS = os.getenv("ENABLE_REAL_TIME_ANALYTICS", "true").lower() == "true"
    ANALYTICS_BATCH_SIZE = int(os.getenv("ANALYTICS_BATCH_SIZE", 1000))
    ANALYTICS_PROCESSING_INTERVAL = int(os.getenv("ANALYTICS_PROCESSING_INTERVAL", 60))  # seconds
    
    # Data processing settings
    MAX_CONCURRENT_QUERIES = int(os.getenv("MAX_CONCURRENT_QUERIES", 10))
    QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT", 300))  # 5 minutes
    CACHE_RESULTS = os.getenv("CACHE_RESULTS", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 hour
    
    # Reporting configuration
    REPORT_FORMATS = os.getenv("REPORT_FORMATS", "json,csv,pdf").split(",")
    ENABLE_SCHEDULED_REPORTS = os.getenv("ENABLE_SCHEDULED_REPORTS", "true").lower() == "true"
    REPORT_STORAGE_PATH = os.getenv("REPORT_STORAGE_PATH", "/app/reports")
    
    # External service dependencies
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    QUEUE_URL = os.getenv("QUEUE_URL", "amqp://localhost:5672")
    STORAGE_URL = os.getenv("STORAGE_URL", "http://localhost:9018")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Metrics collection
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Performance settings
    WORKER_POOL_SIZE = int(os.getenv("WORKER_POOL_SIZE", 4))
    MAX_MEMORY_USAGE = int(os.getenv("MAX_MEMORY_USAGE", 1024 * 1024 * 1024))  # 1GB
    
    # Security settings
    ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    # Monitoring
    ENABLE_SLOW_QUERY_LOGGING = os.getenv("ENABLE_SLOW_QUERY_LOGGING", "true").lower() == "true"
    SLOW_QUERY_THRESHOLD = float(os.getenv("SLOW_QUERY_THRESHOLD", 1.0))  # 1 second

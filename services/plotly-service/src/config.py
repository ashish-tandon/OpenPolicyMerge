"""
Configuration for Plotly Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "plotly-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9011))
    
    # Plotly configuration
    PLOTLY_THEME = os.getenv("PLOTLY_THEME", "plotly_white")
    DEFAULT_COLORS = os.getenv("DEFAULT_COLORS", "plotly").split(",")
    ENABLE_DARK_MODE = os.getenv("ENABLE_DARK_MODE", "true").lower() == "true"
    
    # Chart configuration
    MAX_DATA_POINTS = int(os.getenv("MAX_DATA_POINTS", 10000))
    CHART_CACHE_TTL = int(os.getenv("CHART_CACHE_TTL", 3600))  # 1 hour
    ENABLE_CHART_COMPRESSION = os.getenv("ENABLE_CHART_COMPRESSION", "true").lower() == "true"
    
    # Export configuration
    SUPPORTED_FORMATS = os.getenv("SUPPORTED_FORMATS", "png,jpg,svg,pdf,html").split(",")
    DEFAULT_EXPORT_FORMAT = os.getenv("DEFAULT_EXPORT_FORMAT", "png")
    EXPORT_QUALITY = int(os.getenv("EXPORT_QUALITY", 90))  # percentage
    EXPORT_WIDTH = int(os.getenv("EXPORT_WIDTH", 1200))
    EXPORT_HEIGHT = int(os.getenv("EXPORT_HEIGHT", 800))
    
    # Data processing
    MAX_DATASET_SIZE = int(os.getenv("MAX_DATASET_SIZE", 100 * 1024 * 1024))  # 100MB
    ENABLE_DATA_VALIDATION = os.getenv("ENABLE_DATA_VALIDATION", "true").lower() == "true"
    DATA_CLEANUP_ENABLED = os.getenv("DATA_CLEANUP_ENABLED", "true").lower() == "true"
    
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
    MAX_CONCURRENT_CHARTS = int(os.getenv("MAX_CONCURRENT_CHARTS", 10))
    CHART_GENERATION_TIMEOUT = int(os.getenv("CHART_GENERATION_TIMEOUT", 60))
    
    # Security settings
    ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Monitoring
    ENABLE_SLOW_CHART_LOGGING = os.getenv("ENABLE_SLOW_CHART_LOGGING", "true").lower() == "true"
    SLOW_CHART_THRESHOLD = float(os.getenv("SLOW_CHART_THRESHOLD", 5.0))  # 5 seconds

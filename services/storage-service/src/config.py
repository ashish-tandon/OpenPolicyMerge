"""
Configuration for Storage Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "storage-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9018))
    
    # Storage configuration
    STORAGE_ROOT = os.getenv("STORAGE_ROOT", "/app/storage")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 100 * 1024 * 1024))  # 100MB
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "txt,pdf,doc,docx,xls,xlsx,zip,rar").split(",")
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")  # local, s3, gcs
    
    # S3 configuration (if using S3 backend)
    S3_BUCKET = os.getenv("S3_BUCKET", "openpolicy-storage")
    S3_REGION = os.getenv("S3_REGION", "us-east-1")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
    
    # File retention policy
    DEFAULT_RETENTION_DAYS = int(os.getenv("DEFAULT_RETENTION_DAYS", 365))
    ENABLE_AUTO_CLEANUP = os.getenv("ENABLE_AUTO_CLEANUP", "true").lower() == "true"
    CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", 24))
    
    # Security settings
    ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "false").lower() == "true"
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
    ENABLE_ACCESS_CONTROL = os.getenv("ENABLE_ACCESS_CONTROL", "true").lower() == "true"
    
    # External service dependencies
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    QUEUE_URL = os.getenv("QUEUE_URL", "amqp://localhost:5672")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Metrics collection
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Performance settings
    UPLOAD_CHUNK_SIZE = int(os.getenv("UPLOAD_CHUNK_SIZE", 8 * 1024 * 1024))  # 8MB
    DOWNLOAD_CHUNK_SIZE = int(os.getenv("DOWNLOAD_CHUNK_SIZE", 8 * 1024 * 1024))  # 8MB
    MAX_CONCURRENT_UPLOADS = int(os.getenv("MAX_CONCURRENT_UPLOADS", 10))
    
    # Monitoring
    ENABLE_SLOW_OPERATION_LOGGING = os.getenv("ENABLE_SLOW_OPERATION_LOGGING", "true").lower() == "true"
    SLOW_OPERATION_THRESHOLD = float(os.getenv("SLOW_OPERATION_THRESHOLD", 1.0))  # 1 second

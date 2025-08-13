"""
Configuration for Audit Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "audit-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9014))
    
    # Audit configuration
    AUDIT_LOG_LEVEL = os.getenv("AUDIT_LOG_LEVEL", "INFO")
    AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", 365))
    ENABLE_AUDIT_COMPRESSION = os.getenv("ENABLE_AUDIT_COMPRESSION", "true").lower() == "true"
    AUDIT_BATCH_SIZE = int(os.getenv("AUDIT_BATCH_SIZE", 100))
    
    # Event types to audit
    AUDIT_EVENT_TYPES = os.getenv("AUDIT_EVENT_TYPES", "login,logout,data_access,data_modify,admin_action").split(",")
    ENABLE_REAL_TIME_AUDITING = os.getenv("ENABLE_REAL_TIME_AUDITING", "true").lower() == "true"
    
    # Storage configuration
    AUDIT_STORAGE_BACKEND = os.getenv("AUDIT_STORAGE_BACKEND", "database")  # database, file, elasticsearch
    AUDIT_FILE_PATH = os.getenv("AUDIT_FILE_PATH", "/app/audit_logs")
    AUDIT_DATABASE_TABLE = os.getenv("AUDIT_DATABASE_TABLE", "audit_logs")
    
    # Security settings
    ENABLE_AUDIT_ENCRYPTION = os.getenv("ENABLE_AUDIT_ENCRYPTION", "true").lower() == "true"
    AUDIT_ENCRYPTION_KEY = os.getenv("AUDIT_ENCRYPTION_KEY", "")
    ENABLE_ACCESS_CONTROL = os.getenv("ENABLE_ACCESS_CONTROL", "true").lower() == "true"
    
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
    MAX_CONCURRENT_AUDITS = int(os.getenv("MAX_CONCURRENT_AUDITS", 50))
    AUDIT_PROCESSING_TIMEOUT = int(os.getenv("AUDIT_PROCESSING_TIMEOUT", 30))
    
    # Monitoring
    ENABLE_SLOW_AUDIT_LOGGING = os.getenv("ENABLE_SLOW_AUDIT_LOGGING", "true").lower() == "true"
    SLOW_AUDIT_THRESHOLD = float(os.getenv("SLOW_AUDIT_THRESHOLD", 0.5))  # 500ms

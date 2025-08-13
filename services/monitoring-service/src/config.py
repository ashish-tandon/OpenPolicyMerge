"""
Configuration for Monitoring Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "monitoring-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9010))
    
    # Monitoring configuration
    MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", 60))  # seconds
    ENABLE_REAL_TIME_MONITORING = os.getenv("ENABLE_REAL_TIME_MONITORING", "true").lower() == "true"
    METRICS_RETENTION_DAYS = int(os.getenv("METRICS_RETENTION_DAYS", 30))
    
    # Alert configuration
    ENABLE_ALERTS = os.getenv("ENABLE_ALERTS", "true").lower() == "true"
    ALERT_CHANNELS = os.getenv("ALERT_CHANNELS", "email,slack,webhook").split(",")
    ALERT_THRESHOLD_CPU = float(os.getenv("ALERT_THRESHOLD_CPU", 80.0))  # percentage
    ALERT_THRESHOLD_MEMORY = float(os.getenv("ALERT_THRESHOLD_MEMORY", 80.0))  # percentage
    ALERT_THRESHOLD_DISK = float(os.getenv("ALERT_THRESHOLD_DISK", 85.0))  # percentage
    
    # Service discovery
    SERVICE_DISCOVERY_ENABLED = os.getenv("SERVICE_DISCOVERY_ENABLED", "true").lower() == "true"
    SERVICE_DISCOVERY_INTERVAL = int(os.getenv("SERVICE_DISCOVERY_INTERVAL", 300))  # 5 minutes
    KUBERNETES_ENABLED = os.getenv("KUBERNETES_ENABLED", "true").lower() == "true"
    
    # Metrics collection
    ENABLE_PROMETHEUS = os.getenv("ENABLE_PROMETHEUS", "true").lower() == "true"
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 9090))
    ENABLE_GRAFANA = os.getenv("ENABLE_GRAFANA", "true").lower() == "true"
    GRAFANA_PORT = int(os.getenv("GRAFANA_PORT", 3000))
    
    # External service dependencies
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    QUEUE_URL = os.getenv("QUEUE_URL", "amqp://localhost:5672")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Performance settings
    MAX_CONCURRENT_CHECKS = int(os.getenv("MAX_CONCURRENT_CHECKS", 20))
    CHECK_TIMEOUT = int(os.getenv("CHECK_TIMEOUT", 30))
    
    # Security settings
    ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    ENABLE_SSL = os.getenv("ENABLE_SSL", "false").lower() == "true"
    
    # Monitoring
    ENABLE_SLOW_CHECK_LOGGING = os.getenv("ENABLE_SLOW_CHECK_LOGGING", "true").lower() == "true"
    SLOW_CHECK_THRESHOLD = float(os.getenv("SLOW_CHECK_THRESHOLD", 1.0))  # 1 second

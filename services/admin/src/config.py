"""
Configuration for Admin Dashboard Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "admin-dashboard"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9021))
    
    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))
    
    # Authentication & Authorization
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_EXPIRES_IN = os.getenv("JWT_EXPIRES_IN", "24h")
    ADMIN_ROLE = os.getenv("ADMIN_ROLE", "admin")
    SUPER_ADMIN_ROLE = os.getenv("SUPER_ADMIN_ROLE", "super_admin")
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:9003")
    POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:9001")
    SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:9002")
    ETL_SERVICE_URL = os.getenv("ETL_SERVICE_URL", "http://localhost:9007")
    MONITORING_SERVICE_URL = os.getenv("MONITORING_SERVICE_URL", "http://localhost:9010")
    ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:9013")
    
    # Admin features
    ENABLE_USER_MANAGEMENT = os.getenv("ENABLE_USER_MANAGEMENT", "true").lower() == "true"
    ENABLE_SERVICE_MANAGEMENT = os.getenv("ENABLE_SERVICE_MANAGEMENT", "true").lower() == "true"
    ENABLE_SYSTEM_MONITORING = os.getenv("ENABLE_SYSTEM_MONITORING", "true").lower() == "true"
    ENABLE_AUDIT_LOGS = os.getenv("ENABLE_AUDIT_LOGS", "true").lower() == "true"
    ENABLE_BACKUP_RESTORE = os.getenv("ENABLE_BACKUP_RESTORE", "true").lower() == "true"
    
    # Dashboard configuration
    DASHBOARD_REFRESH_INTERVAL = int(os.getenv("DASHBOARD_REFRESH_INTERVAL", 30000))
    MAX_WIDGETS = int(os.getenv("MAX_WIDGETS", 20))
    ENABLE_REAL_TIME_UPDATES = os.getenv("ENABLE_REAL_TIME_UPDATES", "true").lower() == "true"
    ENABLE_CUSTOM_DASHBOARDS = os.getenv("ENABLE_CUSTOM_DASHBOARDS", "true").lower() == "true"
    
    # Security settings
    ENABLE_2FA = os.getenv("ENABLE_2FA", "true").lower() == "true"
    ENABLE_IP_WHITELIST = os.getenv("ENABLE_IP_WHITELIST", "true").lower() == "true"
    ALLOWED_IPS = os.getenv("ALLOWED_IPS", "127.0.0.1,::1").split(",")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 3600000))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ENABLE_AUDIT_LOG = os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", 90))
    
    # Health check
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30000))
    HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", 5000))
    
    # Performance
    ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    MAX_PAYLOAD_SIZE = int(os.getenv("MAX_PAYLOAD_SIZE", 10 * 1024 * 1024))
    
    # Monitoring
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    ENABLE_PROFILING = os.getenv("ENABLE_PROFILING", "true").lower() == "true"
    ENABLE_ALERTING = os.getenv("ENABLE_ALERTING", "true").lower() == "true"
    
    # Development
    NODE_ENV = os.getenv("NODE_ENV", "development")

# Create config instance
config = Config()

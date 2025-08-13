"""
Configuration for Legacy Django Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "legacy-django"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9022))
    
    # Django configuration
    DJANGO_SETTINGS_MODULE = os.getenv("DJANGO_SETTINGS_MODULE", "represent.settings")
    DJANGO_DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
    DJANGO_SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key-here")
    DJANGO_ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "django.db.backends.postgresql")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "openpolicy")
    DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "password")
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
    
    # Cache configuration
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    CACHE_BACKEND = os.getenv("CACHE_BACKEND", "django_redis.cache.RedisCache")
    CACHE_LOCATION = os.getenv("CACHE_LOCATION", "redis://localhost:6379/1")
    
    # Static files
    STATIC_URL = os.getenv("STATIC_URL", "/static/")
    STATIC_ROOT = os.getenv("STATIC_ROOT", "/app/staticfiles")
    MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
    MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/app/media")
    
    # Security settings
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "false").lower() == "true"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "false").lower() == "true"
    SECURE_BROWSER_XSS_FILTER = os.getenv("SECURE_BROWSER_XSS_FILTER", "true").lower() == "true"
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.getenv("LOG_FILE", "/app/logs/django.log")
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Performance settings
    DEBUG_TOOLBAR = os.getenv("DEBUG_TOOLBAR", "false").lower() == "true"
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:9003")
    POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:9001")
    
    # Legacy features
    ENABLE_LEGACY_APIS = os.getenv("ENABLE_LEGACY_APIS", "true").lower() == "true"
    ENABLE_LEGACY_TEMPLATES = os.getenv("ENABLE_LEGACY_TEMPLATES", "true").lower() == "true"
    ENABLE_LEGACY_ADMIN = os.getenv("ENABLE_LEGACY_ADMIN", "true").lower() == "true"
    
    # Monitoring
    ENABLE_SLOW_QUERY_LOGGING = os.getenv("ENABLE_SLOW_QUERY_LOGGING", "true").lower() == "true"
    SLOW_QUERY_THRESHOLD = float(os.getenv("SLOW_QUERY_THRESHOLD", 1.0))  # 1 second

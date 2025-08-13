"""
Configuration for Web Frontend Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "web-frontend"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9019))
    
    # Next.js configuration
    NEXT_PUBLIC_API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:9001")
    NEXT_PUBLIC_APP_NAME = os.getenv("NEXT_PUBLIC_APP_NAME", "OpenPolicy Platform")
    NEXT_PUBLIC_APP_DESCRIPTION = os.getenv("NEXT_PUBLIC_APP_DESCRIPTION", "Open Policy Platform for Government Transparency")
    
    # Frontend features
    ENABLE_DARK_MODE = os.getenv("ENABLE_DARK_MODE", "true").lower() == "true"
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    ENABLE_PWA = os.getenv("ENABLE_PWA", "true").lower() == "true"
    ENABLE_SSR = os.getenv("ENABLE_SSR", "true").lower() == "true"
    
    # Authentication
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
    AUTH_PROVIDER = os.getenv("AUTH_PROVIDER", "next-auth")
    AUTH_SECRET = os.getenv("AUTH_SECRET", "")
    NEXTAUTH_URL = os.getenv("NEXTAUTH_URL", "http://localhost:9019")
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:9003")
    POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:9001")
    SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:9002")
    ETL_SERVICE_URL = os.getenv("ETL_SERVICE_URL", "http://localhost:9007")
    
    # Performance settings
    BUILD_OPTIMIZATION = os.getenv("BUILD_OPTIMIZATION", "true").lower() == "true"
    ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 hour
    
    # Security settings
    ENABLE_CSP = os.getenv("ENABLE_CSP", "true").lower() == "true"
    ENABLE_HSTS = os.getenv("ENABLE_HSTS", "true").lower() == "true"
    ENABLE_XSS_PROTECTION = os.getenv("ENABLE_XSS_PROTECTION", "true").lower() == "true"
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Monitoring
    ENABLE_PERFORMANCE_MONITORING = os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true"
    ENABLE_ERROR_TRACKING = os.getenv("ENABLE_ERROR_TRACKING", "true").lower() == "true"
    ENABLE_USER_ANALYTICS = os.getenv("ENABLE_USER_ANALYTICS", "true").lower() == "true"
    
    # Development settings
    NODE_ENV = os.getenv("NODE_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOT_RELOAD = os.getenv("HOT_RELOAD", "true").lower() == "true"
    
    # Build settings
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", ".next")
    STATIC_DIR = os.getenv("STATIC_DIR", "public")
    BUILD_ID = os.getenv("BUILD_ID", "")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

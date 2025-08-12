"""
Configuration settings for OpenPolicy Scraper Service
"""
import os
from typing import Dict, Any

class Settings:
    """Application settings"""
    
    # Service configuration
    APP_NAME: str = "OpenPolicy Scraper Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8005"))
    
    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/openpolicy"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    
    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Monitoring configuration
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    
    # Scraper configuration
    MAX_CONCURRENT_SCRAPERS: int = int(os.getenv("MAX_CONCURRENT_SCRAPERS", "10"))
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "300"))
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    
    # Scraper registry (example configuration)
    scraper_registry: Dict[str, Dict[str, Any]] = {
        "parliament_ca": {
            "name": "Parliament of Canada",
            "enabled": True,
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "description": "Federal parliamentary data scraper"
        },
        "ca_on": {
            "name": "Ontario Legislature",
            "enabled": True,
            "schedule": "0 3 * * *",  # Daily at 3 AM
            "description": "Ontario provincial data scraper"
        },
        "ca_on_toronto": {
            "name": "Toronto City Council",
            "enabled": True,
            "schedule": "0 4 * * *",  # Daily at 4 AM
            "description": "Toronto municipal data scraper"
        },
        "ca_bc": {
            "name": "British Columbia Legislature",
            "enabled": True,
            "schedule": "0 5 * * *",  # Daily at 5 AM
            "description": "BC provincial data scraper"
        },
        "ca_ab": {
            "name": "Alberta Legislature",
            "enabled": True,
            "schedule": "0 6 * * *",  # Daily at 6 AM
            "description": "Alberta provincial data scraper"
        },
        "ca_qc": {
            "name": "Quebec Legislature",
            "enabled": True,
            "schedule": "0 7 * * *",  # Daily at 7 AM
            "description": "Quebec provincial data scraper"
        }
    }
    
    # Security configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # External API configuration
    OPENPARLIAMENT_API_URL: str = os.getenv("OPENPARLIAMENT_API_URL", "https://api.openparliament.ca")
    OPENCIVICDATA_API_URL: str = os.getenv("OPENCIVICDATA_API_URL", "https://api.opencivicdata.org")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # File storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    
    # Scraper-specific settings
    SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", "300"))
    SCRAPER_RETRY_DELAY: int = int(os.getenv("SCRAPER_RETRY_DELAY", "60"))
    SCRAPER_MAX_RETRIES: int = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
    
    # Data processing settings
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "1000"))
    PROCESSING_TIMEOUT: int = int(os.getenv("PROCESSING_TIMEOUT", "600"))
    
    # Cache settings
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # Notification settings
    NOTIFICATION_ENABLED: bool = os.getenv("NOTIFICATION_ENABLED", "true").lower() == "true"
    NOTIFICATION_WEBHOOK_URL: str = os.getenv("NOTIFICATION_WEBHOOK_URL", "")
    
    # Health check settings
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    HEALTH_CHECK_TIMEOUT: int = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))
    
    # Swagger configuration
    swagger = type('obj', (object,), {
        'enabled': True
    })()
    
    # CORS configuration
    cors = type('obj', (object,), {
        'origins': ["*"]
    })()
    
    # Monitoring configuration
    monitoring = type('obj', (object,), {
        'enabled': True
    })()
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration as dict"""
        return {
            "url": cls.DATABASE_URL,
            "pool_size": cls.DATABASE_POOL_SIZE,
            "max_overflow": cls.DATABASE_MAX_OVERFLOW
        }
    
    @classmethod
    def get_scraper_config(cls, scraper_id: str) -> Dict[str, Any]:
        """Get configuration for a specific scraper"""
        return cls.scraper_registry.get(scraper_id, {})

# Global settings instance
settings = Settings()

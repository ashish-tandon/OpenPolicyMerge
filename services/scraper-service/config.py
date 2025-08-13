"""
Configuration settings for OpenPolicy Scraper Service
"""
import os
import argparse
from typing import Dict, Any

class Config:
    """Application settings with dual database support"""
    
    def __init__(self):
        """Initialize configuration with command line mode support"""
        self.mode = self._get_mode()
        self._setup_database_urls()
    
    def _get_mode(self) -> str:
        """Get mode from command line arguments or environment variable"""
        parser = argparse.ArgumentParser(description='Scraper Service Mode')
        parser.add_argument('--mode', 
                          choices=['test', 'prod'], 
                          default=os.getenv('SCRAPER_MODE', 'prod'),
                          help='Service mode: test (test DB) or prod (production DB)')
        
        # Parse only known args to avoid conflicts with other services
        args, _ = parser.parse_known_args()
        return args.mode
    
    def _setup_database_urls(self):
        """Setup database URLs based on mode"""
        if self.mode == 'test':
            self.DATABASE_URL = os.getenv(
                "TEST_DATABASE_URL",
                "postgresql://postgres:password@localhost:5432/openpolicy_test"
            )
            self.DATABASE_NAME = "openpolicy_test"
            print(f"🔬 SCRAPER SERVICE RUNNING IN TEST MODE - Using database: {self.DATABASE_NAME}")
        else:
            self.DATABASE_URL = os.getenv(
                "PROD_DATABASE_URL",
                "postgresql://postgres:password@localhost:5432/openpolicy"
            )
            self.DATABASE_NAME = "openpolicy"
            print(f"🚀 SCRAPER SERVICE RUNNING IN PRODUCTION MODE - Using database: {self.DATABASE_NAME}")
    
    # Service configuration
    APP_NAME: str = "OpenPolicy Scraper Service"
    APP_VERSION: str = "2.0.0"  # Updated version for dual DB support
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8005"))
    
    # Database configuration - will be set by _setup_database_urls()
    DATABASE_URL: str = None  # Set dynamically
    DATABASE_NAME: str = None  # Set dynamically
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
    
    # Scraper configuration - Optimized for efficiency
    MAX_CONCURRENT_SCRAPERS: int = int(os.getenv("MAX_CONCURRENT_SCRAPERS", "20"))  # Increased from 10
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "180"))  # Reduced from 300
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "2"))  # Reduced from 3
    
    # Scraper registry (optimized configuration)
    scraper_registry: Dict[str, Dict[str, Any]] = {
        "parliament_ca": {
            "name": "Parliament of Canada",
            "enabled": True,
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "description": "Federal parliamentary data scraper",
            "priority": "high",
            "batch_size": 500  # Optimized batch size
        },
        "ca_on": {
            "name": "Ontario Legislature",
            "enabled": True,
            "schedule": "0 3 * * *",  # Daily at 3 AM
            "description": "Ontario provincial data scraper",
            "priority": "high",
            "batch_size": 500
        },
        "ca_on_toronto": {
            "name": "Toronto City Council",
            "enabled": True,
            "schedule": "0 4 * * *",  # Daily at 4 AM
            "description": "Toronto municipal data scraper",
            "priority": "medium",
            "batch_size": 300
        },
        "ca_bc": {
            "name": "British Columbia Legislature",
            "enabled": True,
            "schedule": "0 5 * * *",  # Daily at 5 AM
            "description": "BC provincial data scraper",
            "priority": "medium",
            "batch_size": 400
        },
        "ca_ab": {
            "name": "Alberta Legislature",
            "enabled": True,
            "schedule": "0 6 * * *",  # Daily at 6 AM
            "description": "Alberta provincial data scraper",
            "priority": "medium",
            "batch_size": 400
        },
        "ca_qc": {
            "name": "Quebec Legislature",
            "enabled": True,
            "schedule": "0 7 * * *",  # Daily at 7 AM
            "description": "Quebec provincial data scraper",
            "priority": "medium",
            "batch_size": 400
        }
    }
    
    # Security configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # External API configuration
    OPENPARLIAMENT_API_URL: str = os.getenv("OPENPARLIAMENT_API_URL", "https://api.openparliament.ca")
    OPENCIVICDATA_API_URL: str = os.getenv("OPENCIVICDATA_API_URL", "https://api.opencivicdata.org")
    
    # Rate limiting - Optimized for efficiency
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))  # Increased from 60
    
    # File storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    
    # Scraper-specific settings - Optimized for efficiency
    SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", "180"))  # Reduced from 300
    SCRAPER_RETRY_DELAY: int = int(os.getenv("SCRAPER_RETRY_DELAY", "30"))  # Reduced from 60
    SCRAPER_MAX_RETRIES: int = int(os.getenv("SCRAPER_MAX_RETRIES", "2"))  # Reduced from 3
    
    # Data processing settings - Optimized for efficiency
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "2000"))  # Increased from 1000
    PROCESSING_TIMEOUT: int = int(os.getenv("PROCESSING_TIMEOUT", "300"))  # Reduced from 600
    
    # Cache settings - Optimized for efficiency
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "7200"))  # Increased from 3600 (2 hours)
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "2000"))  # Increased from 1000
    
    # Notification settings
    NOTIFICATION_ENABLED: bool = os.getenv("NOTIFICATION_ENABLED", "true").lower() == "true"
    NOTIFICATION_WEBHOOK_URL: str = os.getenv("NOTIFICATION_WEBHOOK_URL", "")
    
    # Health check settings
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    HEALTH_CHECK_TIMEOUT: int = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))
    
    # Performance optimization settings
    ENABLE_CONNECTION_POOLING: bool = os.getenv("ENABLE_CONNECTION_POOLING", "true").lower() == "true"
    ENABLE_QUERY_CACHING: bool = os.getenv("ENABLE_QUERY_CACHING", "true").lower() == "true"
    ENABLE_BATCH_PROCESSING: bool = os.getenv("ENABLE_BATCH_PROCESSING", "true").lower() == "true"
    ENABLE_ASYNC_PROCESSING: bool = os.getenv("ENABLE_ASYNC_PROCESSING", "true").lower() == "true"
    
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
            "name": cls.DATABASE_NAME,
            "pool_size": cls.DATABASE_POOL_SIZE,
            "max_overflow": cls.DATABASE_MAX_OVERFLOW,
            "mode": cls.mode
        }
    
    @classmethod
    def get_scraper_config(cls, scraper_id: str) -> Dict[str, Any]:
        """Get configuration for a specific scraper"""
        return cls.scraper_registry.get(scraper_id, {})
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Get mode information for monitoring"""
        return {
            "mode": self.mode,
            "database": self.DATABASE_NAME,
            "database_url": self.DATABASE_URL,
            "optimizations_enabled": {
                "connection_pooling": self.ENABLE_CONNECTION_POOLING,
                "query_caching": self.ENABLE_QUERY_CACHING,
                "batch_processing": self.ENABLE_BATCH_PROCESSING,
                "async_processing": self.ENABLE_ASYNC_PROCESSING
            }
        }

# Global config instance
config = Config()

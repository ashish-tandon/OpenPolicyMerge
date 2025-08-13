"""
Configuration for Scraper Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "scraper-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9008))
    
    # Environment configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
    
    # Database Strategy - Dual Database Approach
    # Test Database (for validation and testing)
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://test_user:test_pass@localhost:5432/test_openpolicy")
    TEST_DATABASE_NAME = os.getenv("TEST_DATABASE_NAME", "test_openpolicy")
    
    # Production Database (for final data)
    PRODUCTION_DATABASE_URL = os.getenv("PRODUCTION_DATABASE_URL", "postgresql://prod_user:prod_pass@localhost:5432/openpolicy")
    PRODUCTION_DATABASE_NAME = os.getenv("PRODUCTION_DATABASE_NAME", "openpolicy")
    
    # Database selection logic
    @property
    def DATABASE_URL(self) -> str:
        """Select database based on environment and test mode"""
        if self.TEST_MODE or self.ENVIRONMENT == "development":
            return self.TEST_DATABASE_URL
        return self.PRODUCTION_DATABASE_URL
    
    @property
    def DATABASE_NAME(self) -> str:
        """Select database name based on environment and test mode"""
        if self.TEST_MODE or self.ENVIRONMENT == "development":
            return self.TEST_DATABASE_NAME
        return self.PRODUCTION_DATABASE_NAME
    
    # Scraping configuration
    SCRAPING_INTERVAL = int(os.getenv("SCRAPING_INTERVAL", 3600))  # 1 hour
    MAX_CONCURRENT_SCRAPERS = int(os.getenv("MAX_CONCURRENT_SCRAPERS", 5))
    SCRAPING_TIMEOUT = int(os.getenv("SCRAPING_TIMEOUT", 300))  # 5 minutes
    
    # Data validation and migration
    ENABLE_SCHEMA_VALIDATION = os.getenv("ENABLE_SCHEMA_VALIDATION", "true").lower() == "true"
    ENABLE_COLUMN_MAPPING = os.getenv("ENABLE_COLUMN_MAPPING", "true").lower() == "true"
    ENABLE_DATA_TRANSFORMATION = os.getenv("ENABLE_DATA_TRANSFORMATION", "true").lower() == "true"
    
    # Test mode specific settings
    TEST_DATA_LIMIT = int(os.getenv("TEST_DATA_LIMIT", 1000))  # Limit data in test mode
    TEST_SCHEMA_VERIFICATION = os.getenv("TEST_SCHEMA_VERIFICATION", "true").lower() == "true"
    TEST_COLUMN_MATCHING = os.getenv("TEST_COLUMN_MATCHING", "true").lower() == "true"
    
    # Production deployment settings
    PRODUCTION_VERIFICATION_REQUIRED = os.getenv("PRODUCTION_VERIFICATION_REQUIRED", "true").lower() == "true"
    PRODUCTION_BACKUP_BEFORE_UPDATE = os.getenv("PRODUCTION_BACKUP_BEFORE_UPDATE", "true").lower() == "true"
    PRODUCTION_ROLLBACK_ENABLED = os.getenv("PRODUCTION_ROLLBACK_ENABLED", "true").lower() == "true"
    
    # External service dependencies
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:9001")
    ETL_SERVICE_URL = os.getenv("ETL_SERVICE_URL", "http://localhost:9007")
    ERROR_REPORTING_URL = os.getenv("ERROR_REPORTING_URL", "http://localhost:9024")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Performance settings
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    MAX_MEMORY_USAGE = int(os.getenv("MAX_MEMORY_USAGE", 1024 * 1024 * 1024))  # 1GB
    
    # Security settings
    ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    # Monitoring
    ENABLE_SLOW_SCRAPING_LOGGING = os.getenv("ENABLE_SLOW_SCRAPING_LOGGING", "true").lower() == "true"
    SLOW_SCRAPING_THRESHOLD = float(os.getenv("SLOW_SCRAPING_THRESHOLD", 10.0))  # 10 seconds

"""
Configuration for OpenPolicy Scraper Service

This service orchestrates all data scraping operations for the OpenPolicy platform,
including parliamentary data, civic data, and external data sources.
"""

import os
from typing import List, Optional, Dict, Any

class ServerSettings:
    def __init__(self):
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8005"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.workers = int(os.getenv("WORKERS", "1"))

class DatabaseSettings:
    def __init__(self):
        self.url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/openpolicy_scrapers")
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"

class RedisSettings:
    def __init__(self):
        self.url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.password = os.getenv("REDIS_PASSWORD")
        self.db = int(os.getenv("REDIS_DB", "0"))

class ScraperSettings:
    def __init__(self):
        # Scraper Configuration
        self.max_concurrent_scrapers = int(os.getenv("MAX_CONCURRENT_SCRAPERS", "5"))
        self.request_delay = float(os.getenv("REQUEST_DELAY", "1.0"))
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.retry_attempts = int(os.getenv("RETRY_ATTEMPTS", "3"))
        
        # User Agent Rotation
        self.user_agents_file = os.getenv("USER_AGENTS_FILE", "user_agents.txt")
        self.rotate_user_agents = os.getenv("ROTATE_USER_AGENTS", "true").lower() == "true"
        
        # Proxy Configuration
        self.use_proxies = os.getenv("USE_PROXIES", "false").lower() == "true"
        self.proxy_list_file = os.getenv("PROXY_LIST_FILE", "proxies.txt")
        
        # Rate Limiting
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.requests_per_minute = int(os.getenv("REQUESTS_PER_MINUTE", "60"))
        
        # Data Storage
        self.data_dir = os.getenv("DATA_DIR", "/app/data")
        self.backup_enabled = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
        self.backup_retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

class MonitoringSettings:
    def __init__(self):
        self.enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.prometheus_enabled = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "9090"))
        self.metrics_path = os.getenv("METRICS_PATH", "/metrics")

class LoggingSettings:
    def __init__(self):
        self.level = os.getenv("LOG_LEVEL", "info")
        self.format = os.getenv("LOG_FORMAT", "json")
        self.file_enabled = os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
        self.file_path = os.getenv("LOG_FILE_PATH", "logs/scraper-service.log")
        self.max_size = os.getenv("LOG_MAX_SIZE", "10MB")
        self.max_files = int(os.getenv("LOG_MAX_FILES", "5"))

class CORSettings:
    def __init__(self):
        self.origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        self.allow_methods = os.getenv("CORS_ALLOW_METHODS", "*").split(",")
        self.allow_headers = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")

class SwaggerSettings:
    def __init__(self):
        self.enabled = os.getenv("SWAGGER_ENABLED", "true").lower() == "true"
        self.title = "OpenPolicy Scraper Service API"
        self.description = "Data scraping and collection service"
        self.version = "1.0.0"

class Settings:
    def __init__(self):
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Server
        self.server = ServerSettings()
        
        # Database
        self.database = DatabaseSettings()
        
        # Redis
        self.redis = RedisSettings()
        
        # Scraper Configuration
        self.scraper = ScraperSettings()
        
        # Monitoring
        self.monitoring = MonitoringSettings()
        
        # Logging
        self.logging = LoggingSettings()
        
        # CORS
        self.cors = CORSettings()
        
        # Swagger
        self.swagger = SwaggerSettings()
        
        # Scraper registry (example configuration)
        self.scraper_registry: Dict[str, Dict[str, Any]] = {
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
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration as dict"""
        return {
            "url": cls().database.url,
            "pool_size": cls().database.pool_size,
            "max_overflow": cls().database.max_overflow
        }
    
    @classmethod
    def get_scraper_config(cls, scraper_id: str) -> Dict[str, Any]:
        """Get configuration for a specific scraper"""
        return cls().scraper_registry.get(scraper_id, {})

# Global settings instance
settings = Settings()

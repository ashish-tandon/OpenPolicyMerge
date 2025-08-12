"""
Configuration for OpenPolicy MCP Service (Model Context Protocol)

This service acts as the middle layer between scrapers and databases,
processing scraped data and injecting it into the appropriate databases.
"""

from pydantic import BaseSettings, Field
from typing import List, Optional, Dict
import os

class ServerSettings(BaseSettings):
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8006, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    workers: int = Field(default=1, env="WORKERS")

class DatabaseSettings(BaseSettings):
    url: str = Field(default="postgresql://postgres:password@localhost:5432/openpolicy", env="DATABASE_URL")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    # Schema configuration for single database approach
    schemas: Dict[str, str] = Field(default={
        "federal": "federal",
        "provincial": "provincial", 
        "municipal": "municipal",
        "representatives": "representatives",
        "bills": "bills",
        "etl": "etl",
        "monitoring": "monitoring",
        "auth": "auth"
    })

class RedisSettings(BaseSettings):
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")

class OPASettings(BaseSettings):
    url: str = Field(default="http://opa:8181", env="OPA_URL")
    enabled: bool = Field(default=True, env="OPA_ENABLED")
    timeout: int = Field(default=30, env="OPA_TIMEOUT")
    
    # Policy paths for different data types
    policies: Dict[str, str] = Field(default={
        "federal": "/policies/federal",
        "provincial": "/policies/provincial",
        "municipal": "/policies/municipal",
        "representatives": "/policies/representatives",
        "bills": "/policies/bills"
    })

class DataProcessingSettings(BaseSettings):
    # Data validation
    validate_data: bool = Field(default=True, env="VALIDATE_DATA")
    strict_validation: bool = Field(default=False, env="STRICT_VALIDATION")
    
    # Data transformation
    transform_data: bool = Field(default=True, env="TRANSFORM_DATA")
    normalize_data: bool = Field(default=True, env="NORMALIZE_DATA")
    
    # Batch processing
    batch_size: int = Field(default=1000, env="BATCH_SIZE")
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    
    # Data quality
    min_quality_score: float = Field(default=0.8, env="MIN_QUALITY_SCORE")
    auto_fix_errors: bool = Field(default=True, env="AUTO_FIX_ERRORS")

class DataSourceSettings(BaseSettings):
    # Data source configuration
    sources: Dict[str, Dict] = Field(default={
        "federal": {
            "name": "Federal Parliament",
            "enabled": True,
            "priority": "high",
            "update_frequency": "daily",
            "data_types": ["bills", "representatives", "votes", "committees"]
        },
        "provincial": {
            "name": "Provincial Legislatures",
            "enabled": True,
            "priority": "high",
            "update_frequency": "daily",
            "data_types": ["bills", "representatives", "votes", "committees"],
            "provinces": ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"]
        },
        "municipal": {
            "name": "Municipal Councils",
            "enabled": True,
            "priority": "medium",
            "update_frequency": "weekly",
            "data_types": ["representatives", "meetings", "resolutions"],
            "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Edmonton", "Ottawa"]
        },
        "openparliament": {
            "name": "OpenParliament",
            "enabled": True,
            "priority": "high",
            "update_frequency": "daily",
            "data_types": ["bills", "representatives", "votes", "committees", "debates"]
        },
        "opennorth": {
            "name": "OpenNorth",
            "enabled": True,
            "priority": "high",
            "update_frequency": "weekly",
            "data_types": ["representatives", "boundaries", "elections"]
        }
    })

class MonitoringSettings(BaseSettings):
    enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    metrics_path: str = Field(default="/metrics", env="METRICS_PATH")

class LoggingSettings(BaseSettings):
    level: str = Field(default="info", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    file_enabled: bool = Field(default=True, env="LOG_FILE_ENABLED")
    file_path: str = Field(default="logs/mcp-service.log", env="LOG_FILE_PATH")
    max_size: str = Field(default="10MB", env="LOG_MAX_SIZE")
    max_files: int = Field(default=5, env="LOG_MAX_FILES")

class CORSettings(BaseSettings):
    origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

class SwaggerSettings(BaseSettings):
    enabled: bool = Field(default=True, env="SWAGGER_ENABLED")
    title: str = Field(default="OpenPolicy MCP Service API")
    description: str = Field(default="Model Context Protocol service for data processing")
    version: str = Field(default="1.0.0")

class Settings(BaseSettings):
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    server: ServerSettings = ServerSettings()
    
    # Database
    database: DatabaseSettings = DatabaseSettings()
    
    # Redis
    redis: RedisSettings = RedisSettings()
    
    # OPA Integration
    opa: OPASettings = OPASettings()
    
    # Data Processing
    data_processing: DataProcessingSettings = DataProcessingSettings()
    
    # Data Sources
    data_sources: DataSourceSettings = DataSourceSettings()
    
    # Monitoring
    monitoring: MonitoringSettings = MonitoringSettings()
    
    # Logging
    logging: LoggingSettings = LoggingSettings()
    
    # CORS
    cors: CORSettings = CORSettings()
    
    # Swagger
    swagger: SwaggerSettings = SwaggerSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Environment-specific overrides
if settings.environment == "production":
    settings.debug = False
    settings.logging.level = "warn"
    settings.swagger.enabled = False
    settings.cors.origins = ["https://yourdomain.com"]
    settings.data_processing.batch_size = 5000
    settings.data_processing.max_workers = 8
elif settings.environment == "test":
    settings.database.url = "postgresql://postgres:password@localhost:5432/openpolicy_test"
    settings.redis.db = 1
    settings.logging.level = "debug"
    settings.data_processing.batch_size = 100
    settings.data_processing.max_workers = 2

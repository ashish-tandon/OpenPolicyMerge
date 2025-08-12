"""
Configuration management for the OpenPolicy ETL service.
"""
import os
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    username: str = Field(default="postgres", env="DB_USERNAME")
    password: str = Field(default="postgres", env="DB_PASSWORD")
    database: str = Field(default="openpolicy_etl", env="DB_NAME")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    @property
    def url(self) -> str:
        """Generate database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    @property
    def url(self) -> str:
        """Generate Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = "REDIS_"


class CelerySettings(BaseSettings):
    """Celery configuration settings."""
    
    broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    accept_content: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    timezone: str = Field(default="UTC", env="CELERY_TIMEZONE")
    enable_utc: bool = Field(default=True, env="CELERY_ENABLE_UTC")
    worker_prefetch_multiplier: int = Field(default=1, env="CELERY_WORKER_PREFETCH_MULTIPLIER")
    task_acks_late: bool = Field(default=True, env="CELERY_TASK_ACKS_LATE")
    worker_max_tasks_per_child: int = Field(default=1000, env="CELERY_WORKER_MAX_TASKS_PER_CHILD")
    
    class Config:
        env_prefix = "CELERY_"


class APISettings(BaseSettings):
    """API configuration settings."""
    
    title: str = Field(default="OpenPolicy ETL Service", env="API_TITLE")
    version: str = Field(default="1.0.0", env="API_VERSION")
    description: str = Field(default="ETL service for OpenPolicy data processing", env="API_DESCRIPTION")
    debug: bool = Field(default=False, env="API_DEBUG")
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8003, env="API_PORT")
    cors_origins: List[str] = Field(default=["*"], env="API_CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="API_CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="API_CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="API_CORS_ALLOW_HEADERS")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_prefix = "API_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_size: str = Field(default="100MB", env="LOG_MAX_SIZE")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    rotation: str = Field(default="1 day", env="LOG_ROTATION")
    
    class Config:
        env_prefix = "LOG_"


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""
    
    enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    opentelemetry_enabled: bool = Field(default=True, env="OPENTELEMETRY_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=10, env="HEALTH_CHECK_TIMEOUT")
    
    class Config:
        env_prefix = "MONITORING_"


class ETLSettings(BaseSettings):
    """ETL-specific configuration settings."""
    
    # Data Sources
    parliamentary_data_url: str = Field(default="https://api.parliament.uk", env="ETL_PARLIAMENTARY_DATA_URL")
    civic_data_url: str = Field(default="https://api.civicdata.com", env="ETL_CIVIC_DATA_URL")
    government_data_url: str = Field(default="https://data.gov.uk", env="ETL_GOVERNMENT_DATA_URL")
    
    # Processing Settings
    batch_size: int = Field(default=1000, env="ETL_BATCH_SIZE")
    max_workers: int = Field(default=4, env="ETL_MAX_WORKERS")
    timeout: int = Field(default=300, env="ETL_TIMEOUT")
    retry_attempts: int = Field(default=3, env="ETL_RETRY_ATTEMPTS")
    retry_delay: int = Field(default=60, env="ETL_RETRY_DELAY")
    
    # Storage Settings
    data_dir: str = Field(default="/app/data", env="ETL_DATA_DIR")
    temp_dir: str = Field(default="/app/temp", env="ETL_TEMP_DIR")
    archive_dir: str = Field(default="/app/archive", env="ETL_ARCHIVE_DIR")
    
    # Schedule Settings
    default_schedule: str = Field(default="0 */6 * * *", env="ETL_DEFAULT_SCHEDULE")  # Every 6 hours
    cleanup_schedule: str = Field(default="0 2 * * *", env="ETL_CLEANUP_SCHEDULE")    # Daily at 2 AM
    
    # Data Retention
    retention_days: int = Field(default=90, env="ETL_RETENTION_DAYS")
    max_file_size: str = Field(default="1GB", env="ETL_MAX_FILE_SIZE")
    
    class Config:
        env_prefix = "ETL_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(default="your-super-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="SECURITY_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=900, env="RATE_LIMIT_WINDOW")  # 15 minutes
    
    class Config:
        env_prefix = "SECURITY_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Service Configuration
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    celery: CelerySettings = CelerySettings()
    api: APISettings = APISettings()
    logging: LoggingSettings = LoggingSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    etl: ETLSettings = ETLSettings()
    security: SecuritySettings = SecuritySettings()
    
    # Feature Flags
    features: Dict[str, bool] = Field(default={
        "data_validation": True,
        "data_transformation": True,
        "data_loading": True,
        "scheduling": True,
        "monitoring": True,
        "notifications": True
    }, env="FEATURES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set debug mode based on environment
        if self.environment == "development":
            self.debug = True
            self.api.debug = True
            self.logging.level = "DEBUG"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> None:
    """Reload settings from environment."""
    global settings
    settings = Settings()

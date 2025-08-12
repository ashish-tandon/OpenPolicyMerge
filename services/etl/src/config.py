"""
Configuration management for the OpenPolicy ETL service.
"""
import os
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator
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
    
    @field_validator("cors_origins", mode="before")
    @classmethod
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
    max_files: int = Field(default=5, env="LOG_MAX_FILES")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    class Config:
        env_prefix = "LOG_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_max_requests: int = Field(default=100, env="RATE_LIMIT_MAX_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, env="RATE_LIMIT_WINDOW_SECONDS")
    
    class Config:
        env_prefix = "SECURITY_"


class MonitoringSettings(BaseSettings):
    """Monitoring configuration settings."""
    
    enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    metrics_path: str = Field(default="/metrics", env="METRICS_PATH")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=10, env="HEALTH_CHECK_TIMEOUT")
    
    class Config:
        env_prefix = "MONITORING_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Service settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    celery: CelerySettings = CelerySettings()
    api: APISettings = APISettings()
    logging: LoggingSettings = LoggingSettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings

"""
Configuration for OpenPolicy Health Service
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os

class ServerSettings(BaseSettings):
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8005, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    workers: int = Field(default=1, env="WORKERS")

class DatabaseSettings(BaseSettings):
    url: str = Field(default="postgresql://postgres:password@localhost:5432/openpolicy_health", env="DATABASE_URL")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")

class RedisSettings(BaseSettings):
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")

class MonitoringSettings(BaseSettings):
    enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    metrics_path: str = Field(default="/metrics", env="METRICS_PATH")

class HealthCheckSettings(BaseSettings):
    interval: int = Field(default=30000, env="HEALTH_CHECK_INTERVAL")  # 30 seconds
    timeout: int = Field(default=10000, env="HEALTH_CHECK_TIMEOUT")    # 10 seconds
    retries: int = Field(default=3, env="HEALTH_CHECK_RETRIES")
    failure_threshold: int = Field(default=3, env="FAILURE_THRESHOLD")
    recovery_threshold: int = Field(default=2, env="RECOVERY_THRESHOLD")

class AlertSettings(BaseSettings):
    enabled: bool = Field(default=True, env="ALERTS_ENABLED")
    email_enabled: bool = Field(default=False, env="EMAIL_ALERTS_ENABLED")
    webhook_enabled: bool = Field(default=True, env="WEBHOOK_ALERTS_ENABLED")
    slack_enabled: bool = Field(default=False, env="SLACK_ALERTS_ENABLED")
    escalation_enabled: bool = Field(default=True, env="ESCALATION_ENABLED")

class ServiceDiscoverySettings(BaseSettings):
    enabled: bool = Field(default=True, env="SERVICE_DISCOVERY_ENABLED")
    auto_discovery: bool = Field(default=True, env="AUTO_DISCOVERY_ENABLED")
    discovery_interval: int = Field(default=60000, env="DISCOVERY_INTERVAL")  # 1 minute
    service_registry_url: Optional[str] = Field(default=None, env="SERVICE_REGISTRY_URL")

class LoggingSettings(BaseSettings):
    level: str = Field(default="info", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    file_enabled: bool = Field(default=True, env="LOG_FILE_ENABLED")
    file_path: str = Field(default="logs/health-service.log", env="LOG_FILE_PATH")
    max_size: str = Field(default="10MB", env="LOG_MAX_SIZE")
    max_files: int = Field(default=5, env="LOG_MAX_FILES")

class CORSettings(BaseSettings):
    origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

class SwaggerSettings(BaseSettings):
    enabled: bool = Field(default=True, env="SWAGGER_ENABLED")
    title: str = Field(default="OpenPolicy Health Service API")
    description: str = Field(default="Health monitoring and alerting service")
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
    
    # Monitoring
    monitoring: MonitoringSettings = MonitoringSettings()
    
    # Health Checks
    health_check: HealthCheckSettings = HealthCheckSettings()
    
    # Alerts
    alerts: AlertSettings = AlertSettings()
    
    # Service Discovery
    service_discovery: ServiceDiscoverySettings = ServiceDiscoverySettings()
    
    # Logging
    logging: LoggingSettings = LoggingSettings()
    
    # CORS
    cors: CORSettings = CORSettings()
    
    # Swagger
    swagger: SwaggerSettings = SwaggerSettings()
    
    # Service URLs (for health checks)
    service_urls: dict = Field(default={
        "api-gateway": "http://localhost:8000",
        "etl-service": "http://localhost:8003",
        "plotly-service": "http://localhost:8004",
        "mobile-api": "http://localhost:8002",
        "frontend": "http://localhost:3000",
        "admin-dashboard": "http://localhost:8002",
        "go-api": "http://localhost:8080"
    })
    
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
elif settings.environment == "test":
    settings.database.url = "postgresql://postgres:password@localhost:5432/openpolicy_health_test"
    settings.redis.db = 1
    settings.logging.level = "debug"

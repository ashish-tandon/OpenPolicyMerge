"""
Configuration for OPA Service
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Service Configuration
    service_name: str = "opa-service"
    service_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8181
    
    # Database Configuration
    database_url: Optional[str] = None
    
    # Redis Configuration
    redis_url: Optional[str] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Policy Engine Configuration
    max_policies: int = 1000
    policy_cache_size: int = 100
    evaluation_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

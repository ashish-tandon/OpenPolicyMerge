"""
Configuration for MCP Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "mcp-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9012))
    
    # MCP configuration
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", 9012))
    MCP_PROTOCOL_VERSION = os.getenv("MCP_PROTOCOL_VERSION", "1.0")
    MCP_ENABLE_TLS = os.getenv("MCP_ENABLE_TLS", "false").lower() == "true"
    
    # Model configuration
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    TOP_P = float(os.getenv("TOP_P", 1.0))
    
    # API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_API_BASE = os.getenv("ANTHROPIC_API_BASE", "https://api.anthropic.com")
    
    # Rate limiting
    REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", 60))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    
    # External service dependencies
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    QUEUE_URL = os.getenv("QUEUE_URL", "amqp://localhost:5672")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Metrics collection
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Performance settings
    WORKER_POOL_SIZE = int(os.getenv("WORKER_POOL_SIZE", 4))
    MAX_MEMORY_USAGE = int(os.getenv("MAX_MEMORY_USAGE", 1024 * 1024 * 1024))  # 1GB
    
    # Security settings
    ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    
    # Monitoring
    ENABLE_SLOW_REQUEST_LOGGING = os.getenv("ENABLE_SLOW_REQUEST_LOGGING", "true").lower() == "true"
    SLOW_REQUEST_THRESHOLD = float(os.getenv("SLOW_REQUEST_THRESHOLD", 2.0))  # 2 seconds

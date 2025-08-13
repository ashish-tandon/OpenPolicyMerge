"""
Configuration for Queue Service
"""
import os
from typing import Optional

class Config:
    """Service configuration"""
    
    # Service identification
    SERVICE_NAME = "queue-service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9017))
    
    # RabbitMQ configuration
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
    RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
    
    # Queue configuration
    DEFAULT_QUEUE = os.getenv("DEFAULT_QUEUE", "openpolicy_tasks")
    DEFAULT_EXCHANGE = os.getenv("DEFAULT_EXCHANGE", "openpolicy_exchange")
    DEFAULT_ROUTING_KEY = os.getenv("DEFAULT_ROUTING_KEY", "openpolicy.task")
    
    # Task configuration
    MAX_TASK_RETRIES = int(os.getenv("MAX_TASK_RETRIES", 3))
    TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", 300))  # 5 minutes
    WORKER_POOL_SIZE = int(os.getenv("WORKER_POOL_SIZE", 4))
    
    # External service dependencies
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
    
    # Metrics collection
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Performance settings
    CONNECTION_POOL_SIZE = int(os.getenv("CONNECTION_POOL_SIZE", 10))
    CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", 30))
    CONNECTION_RETRY_ATTEMPTS = int(os.getenv("CONNECTION_RETRY_ATTEMPTS", 3))
    
    # Queue policies
    ENABLE_DEAD_LETTER_QUEUE = os.getenv("ENABLE_DEAD_LETTER_QUEUE", "true").lower() == "true"
    DEAD_LETTER_EXCHANGE = os.getenv("DEAD_LETTER_EXCHANGE", "openpolicy_dlx")
    MESSAGE_TTL = int(os.getenv("MESSAGE_TTL", 86400))  # 24 hours
    
    # Monitoring
    ENABLE_SLOW_TASK_LOGGING = os.getenv("ENABLE_SLOW_TASK_LOGGING", "true").lower() == "true"
    SLOW_TASK_THRESHOLD = float(os.getenv("SLOW_TASK_THRESHOLD", 1.0))  # 1 second

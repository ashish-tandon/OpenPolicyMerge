"""
Logging configuration for the ETL service.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from structlog import configure, processors, stdlib

from config import get_settings

# Get settings
settings = get_settings()


def setup_logging():
    """Setup logging configuration."""
    
    # Remove default loguru handler
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.logging.file_path).parent if settings.logging.file_path else Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.logging.level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File logging
    if settings.logging.file_path:
        logger.add(
            settings.logging.file_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.logging.level,
            rotation=settings.logging.rotation,
            retention=settings.logging.backup_count,
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    # Error logging to separate file
    error_log_path = log_dir / "errors.log"
    logger.add(
        error_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention=30,
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Performance logging
    perf_log_path = log_dir / "performance.log"
    logger.add(
        perf_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        filter=lambda record: "performance" in record["extra"],
        rotation="1 day",
        retention=7,
        compression="zip"
    )
    
    # Security logging
    security_log_path = log_dir / "security.log"
    logger.add(
        security_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        filter=lambda record: "security" in record["extra"],
        rotation="1 day",
        retention=90,
        compression="zip"
    )
    
    # Setup structlog for structured logging
    configure(
        processors=[
            stdlib.filter_by_level,
            stdlib.add_logger_name,
            stdlib.add_log_level,
            stdlib.PositionalArgumentsFormatter(),
            processors.TimeStamper(fmt="iso"),
            processors.StackInfoRenderer(),
            processors.format_exc_info,
            processors.UnicodeDecoder(),
            stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=stdlib.LoggerFactory(),
        wrapper_class=stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Log startup message
    logger.info("🚀 ETL Service logging initialized", 
                extra={"service": "etl", "environment": settings.environment})


def get_logger(name: str = None):
    """Get a logger instance."""
    return logger.bind(name=name or "etl")


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics."""
    logger.info(f"Performance: {operation} completed in {duration:.2f}s",
                extra={"performance": True, "operation": operation, "duration": duration, **kwargs})


def log_security(event: str, user_id: str = None, ip_address: str = None, **kwargs):
    """Log security events."""
    logger.info(f"Security: {event}",
                extra={"security": True, "event": event, "user_id": user_id, "ip_address": ip_address, **kwargs})


def log_data_quality(metric: str, value: float, status: str, **kwargs):
    """Log data quality metrics."""
    logger.info(f"Data Quality: {metric} = {value} ({status})",
                extra={"data_quality": True, "metric": metric, "value": value, "status": status, **kwargs})


def log_etl_job(job_id: str, operation: str, **kwargs):
    """Log ETL job operations."""
    logger.info(f"ETL Job {job_id}: {operation}",
                extra={"etl_job": True, "job_id": job_id, "operation": operation, **kwargs})


def log_data_source(source_id: str, operation: str, **kwargs):
    """Log data source operations."""
    logger.info(f"Data Source {source_id}: {operation}",
                extra={"data_source": True, "source_id": source_id, "operation": operation, **kwargs})


# Custom log levels
logger.level("PERFORMANCE", no=25, color="<blue>")
logger.level("SECURITY", no=26, color="<red>")
logger.level("DATA_QUALITY", no=27, color="<yellow>")
logger.level("ETL_JOB", no=28, color="<magenta>")
logger.level("DATA_SOURCE", no=29, color="<cyan>")


# Context manager for timing operations
class PerformanceLogger:
    """Context manager for logging performance metrics."""
    
    def __init__(self, operation: str, logger_name: str = None):
        self.operation = operation
        self.logger = get_logger(logger_name)
        self.start_time = None
    
    def __enter__(self):
        self.start_time = logger.bind()._time()
        self.logger.info(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = logger.bind()._time() - self.start_time
            if exc_type:
                self.logger.error(f"Failed: {self.operation} after {duration:.2f}s", 
                                extra={"error": str(exc_val)})
            else:
                self.logger.info(f"Completed: {self.operation} in {duration:.2f}s")
                log_performance(self.operation, duration)


# Decorator for logging function performance
def log_performance_decorator(operation: str = None):
    """Decorator to log function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation or f"{func.__module__}.{func.__name__}"
            with PerformanceLogger(op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Structured logging helpers
def log_structured(level: str, message: str, **kwargs):
    """Log structured data."""
    extra_data = {
        "timestamp": logger.bind()._time(),
        "level": level.upper(),
        "message": message,
        **kwargs
    }
    
    if level.upper() == "ERROR":
        logger.error(message, extra=extra_data)
    elif level.upper() == "WARNING":
        logger.warning(message, extra=extra_data)
    elif level.upper() == "INFO":
        logger.info(message, extra=extra_data)
    else:
        logger.debug(message, extra=extra_data)


def log_request(request_id: str, method: str, path: str, status_code: int, duration: float, **kwargs):
    """Log HTTP request details."""
    logger.info(f"HTTP Request: {method} {path} - {status_code} ({duration:.2f}s)",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration": duration,
                    "type": "http_request",
                    **kwargs
                })


def log_database_operation(operation: str, table: str, duration: float, rows_affected: int = None, **kwargs):
    """Log database operation details."""
    logger.info(f"Database: {operation} on {table} ({duration:.2f}s)",
                extra={
                    "operation": operation,
                    "table": table,
                    "duration": duration,
                    "rows_affected": rows_affected,
                    "type": "database_operation",
                    **kwargs
                })


def log_cache_operation(operation: str, key: str, hit: bool, duration: float = None, **kwargs):
    """Log cache operation details."""
    status = "HIT" if hit else "MISS"
    message = f"Cache {operation}: {key} - {status}"
    if duration:
        message += f" ({duration:.3f}s)"
    
    logger.info(message,
                extra={
                    "operation": operation,
                    "key": key,
                    "hit": hit,
                    "duration": duration,
                    "type": "cache_operation",
                    **kwargs
                })

"""
Enhanced Logging Configuration for OpenPolicy Scraper Service

This module provides comprehensive logging configuration for all services.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json
import traceback

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
MAIN_LOG_FILE = LOGS_DIR / "openpolicy_scraper.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"
PERFORMANCE_LOG_FILE = LOGS_DIR / "performance.log"
DATABASE_LOG_FILE = LOGS_DIR / "database.log"
SCRAPER_LOG_FILE = LOGS_DIR / "scrapers.log"
ETL_LOG_FILE = LOGS_DIR / "etl.log"

# Log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Default log level
DEFAULT_LOG_LEVEL = "INFO"

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # Add timestamp
        record.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Add process and thread info
        record.process_info = f"[PID:{record.process}][TID:{record.thread}]"
        
        # Add module and function info
        record.module_info = f"{record.module}:{record.funcName}:{record.lineno}"
        
        return super().format(record)

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
            "message": record.getMessage(),
            "extra": getattr(record, 'extra_data', {}),
            "exception": None
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry, indent=2)

class PerformanceFilter(logging.Filter):
    """Filter for performance-related log messages."""
    
    def filter(self, record):
        return (
            "performance" in record.getMessage().lower() or
            "timing" in record.getMessage().lower() or
            "duration" in record.getMessage().lower() or
            "throughput" in record.getMessage().lower() or
            "latency" in record.getMessage().lower()
        )

class DatabaseFilter(logging.Filter):
    """Filter for database-related log messages."""
    
    def filter(self, record):
        return (
            "database" in record.getMessage().lower() or
            "sql" in record.getMessage().lower() or
            "query" in record.getMessage().lower() or
            "connection" in record.getMessage().lower() or
            "transaction" in record.getMessage().lower()
        )

class ScraperFilter(logging.Filter):
    """Filter for scraper-related log messages."""
    
    def filter(self, record):
        return (
            "scraper" in record.getMessage().lower() or
            "crawl" in record.getMessage().lower() or
            "extract" in record.getMessage().lower() or
            "parse" in record.getMessage().lower() or
            "collect" in record.getMessage().lower()
        )

class ETLErrorFilter(logging.Filter):
    """Filter for ETL error messages."""
    
    def filter(self, record):
        return (
            record.levelno >= logging.ERROR and
            ("etl" in record.getMessage().lower() or
             "pipeline" in record.getMessage().lower() or
             "transform" in record.getMessage().lower() or
             "load" in record.getMessage().lower())
        )

def setup_logging(
    log_level: str = DEFAULT_LOG_LEVEL,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_structured: bool = False,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> Dict[str, logging.Logger]:
    """Setup comprehensive logging for all services."""
    
    # Set root log level
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS.get(log_level.upper(), LOG_LEVELS[DEFAULT_LOG_LEVEL]))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = ColoredFormatter(
        '%(timestamp)s %(levelname)s %(process_info)s %(module_info)s - %(message)s'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
    )
    
    structured_formatter = StructuredFormatter()
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVELS.get(log_level.upper(), LOG_LEVELS[DEFAULT_LOG_LEVEL]))
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file:
        # Main log file with rotation
        main_handler = logging.handlers.RotatingFileHandler(
            MAIN_LOG_FILE,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(file_formatter)
        root_logger.addHandler(main_handler)
        
        # Error log file
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
        
        # Performance log file
        perf_handler = logging.handlers.RotatingFileHandler(
            PERFORMANCE_LOG_FILE,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(file_formatter)
        perf_handler.addFilter(PerformanceFilter())
        root_logger.addHandler(perf_handler)
        
        # Database log file
        db_handler = logging.handlers.RotatingFileHandler(
            DATABASE_LOG_FILE,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        db_handler.setLevel(logging.INFO)
        db_handler.setFormatter(file_formatter)
        db_handler.addFilter(DatabaseFilter())
        root_logger.addHandler(db_handler)
        
        # Scraper log file
        scraper_handler = logging.handlers.RotatingFileHandler(
            SCRAPER_LOG_FILE,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        scraper_handler.setLevel(logging.INFO)
        scraper_handler.setFormatter(file_formatter)
        scraper_handler.addFilter(ScraperFilter())
        root_logger.addHandler(scraper_handler)
        
        # ETL log file
        etl_handler = logging.handlers.RotatingFileHandler(
            ETL_LOG_FILE,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        etl_handler.setLevel(logging.INFO)
        etl_handler.setFormatter(file_formatter)
        root_logger.addHandler(etl_handler)
    
    # Structured logging handler
    if enable_structured:
        structured_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "structured.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        structured_handler.setLevel(logging.DEBUG)
        structured_handler.setFormatter(structured_formatter)
        root_logger.addHandler(structured_handler)
    
    # Create service loggers
    loggers = {}
    
    # Core service loggers
    loggers['scraper_manager'] = logging.getLogger('src.services.scraper_manager')
    loggers['data_pipeline'] = logging.getLogger('src.services.data_pipeline')
    loggers['etl_service'] = logging.getLogger('src.services.etl_service')
    loggers['performance_monitor'] = logging.getLogger('src.services.performance_monitor')
    loggers['coverage_validator'] = logging.getLogger('src.services.coverage_validator')
    
    # Database logger
    loggers['database'] = logging.getLogger('src.core.database')
    
    # Main application logger
    loggers['main'] = logging.getLogger('openpolicy_scraper')
    
    # Set specific levels for service loggers
    for logger in loggers.values():
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # Prevent duplicate logging
    
        # Add handlers to service loggers
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(LOG_LEVELS.get(log_level.upper(), LOG_LEVELS[DEFAULT_LOG_LEVEL]))
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        if enable_file:
            file_handler = logging.handlers.RotatingFileHandler(
                MAIN_LOG_FILE,
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
    
    # Log startup message
    startup_logger = logging.getLogger('openpolicy_scraper.startup')
    startup_logger.info("🚀 OpenPolicy Scraper Service Logging System Initialized")
    startup_logger.info(f"📁 Log files directory: {LOGS_DIR.absolute()}")
    startup_logger.info(f"🔧 Log level: {log_level.upper()}")
    startup_logger.info(f"📊 Console logging: {'enabled' if enable_console else 'disabled'}")
    startup_logger.info(f"💾 File logging: {'enabled' if enable_file else 'disabled'}")
    startup_logger.info(f"📋 Structured logging: {'enabled' if enable_structured else 'disabled'}")
    
    return loggers

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)

def log_function_call(func):
    """Decorator to log function calls with parameters and timing."""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"{func.__module__}.{func.__name__}")
        
        # Log function entry
        logger.debug(f"🔵 Function called: {func.__name__}")
        logger.debug(f"📥 Arguments: args={args}, kwargs={kwargs}")
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Log successful completion
            logger.debug(f"✅ Function completed: {func.__name__} in {duration:.4f}s")
            logger.debug(f"📤 Return value: {result}")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Log error
            logger.error(f"❌ Function failed: {func.__name__} after {duration:.4f}s")
            logger.error(f"🚨 Error: {type(e).__name__}: {str(e)}")
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            
            raise
    
    return wrapper

def log_performance(operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
    """Log performance metrics."""
    logger = logging.getLogger('performance')
    
    log_data = {
        "operation": operation,
        "duration": duration,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    
    if duration > 1.0:  # Log slow operations as warnings
        logger.warning(f"🐌 Slow operation detected: {operation} took {duration:.4f}s")
    else:
        logger.info(f"⚡ Performance: {operation} completed in {duration:.4f}s")
    
    logger.debug(f"📊 Performance details: {json.dumps(log_data, indent=2)}")

def log_database_operation(operation: str, table: str, duration: float, rows_affected: int = 0):
    """Log database operations."""
    logger = logging.getLogger('database')
    
    logger.info(f"🗄️ Database operation: {operation} on {table}")
    logger.info(f"⏱️ Duration: {duration:.4f}s")
    logger.info(f"📊 Rows affected: {rows_affected}")
    
    if duration > 0.5:  # Log slow queries as warnings
        logger.warning(f"🐌 Slow database operation: {operation} on {table} took {duration:.4f}s")

def log_scraper_activity(scraper_id: int, action: str, details: Dict[str, Any]):
    """Log scraper activities."""
    logger = logging.getLogger('scrapers')
    
    logger.info(f"🕷️ Scraper {scraper_id}: {action}")
    logger.info(f"📋 Details: {json.dumps(details, indent=2)}")

def log_etl_operation(operation: str, stage: str, details: Dict[str, Any]):
    """Log ETL operations."""
    logger = logging.getLogger('etl')
    
    logger.info(f"🔄 ETL {stage}: {operation}")
    logger.info(f"📋 Details: {json.dumps(details, indent=2)}")

def log_error(error: Exception, context: str = "", extra_data: Optional[Dict[str, Any]] = None):
    """Log errors with context and extra data."""
    logger = logging.getLogger('errors')
    
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "timestamp": datetime.now().isoformat(),
        "traceback": traceback.format_exc(),
        "extra_data": extra_data or {}
    }
    
    logger.error(f"🚨 Error in {context}: {type(error).__name__}: {str(error)}")
    logger.error(f"📍 Traceback: {traceback.format_exc()}")
    logger.debug(f"📋 Error details: {json.dumps(error_data, indent=2)}")

def log_system_health(component: str, status: str, details: Optional[Dict[str, Any]] = None):
    """Log system health information."""
    logger = logging.getLogger('health')
    
    status_emoji = {
        "healthy": "✅",
        "warning": "⚠️",
        "error": "❌",
        "degraded": "🟡"
    }.get(status.lower(), "❓")
    
    logger.info(f"{status_emoji} {component}: {status}")
    if details:
        logger.debug(f"📋 Health details: {json.dumps(details, indent=2)}")

def cleanup_logs(max_age_days: int = 30):
    """Clean up old log files."""
    logger = logging.getLogger('maintenance')
    
    current_time = datetime.now()
    deleted_count = 0
    
    for log_file in LOGS_DIR.glob("*.log.*"):
        try:
            file_age = current_time - datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_age.days > max_age_days:
                log_file.unlink()
                deleted_count += 1
                logger.info(f"🗑️ Deleted old log file: {log_file.name}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete old log file {log_file.name}: {e}")
    
    logger.info(f"🧹 Log cleanup completed: {deleted_count} old files deleted")

# Initialize logging when module is imported
if __name__ == "__main__":
    # Test logging setup
    loggers = setup_logging(
        log_level="DEBUG",
        enable_console=True,
        enable_file=True,
        enable_structured=True
    )
    
    # Test various logging functions
    test_logger = logging.getLogger('test')
    test_logger.info("🧪 Testing logging system")
    
    log_performance("test_operation", 0.5, {"test": True})
    log_database_operation("SELECT", "test_table", 0.1, 5)
    log_scraper_activity(1, "started", {"url": "http://test.com"})
    log_etl_operation("extract", "data_extraction", {"source": "test"})
    log_system_health("test_component", "healthy", {"uptime": 3600})
    
    print("✅ Logging system test completed successfully!")

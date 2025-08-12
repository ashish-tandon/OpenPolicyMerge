"""
Monitoring and observability setup for the ETL service.
"""
import os
import time
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from config import get_settings

# Get settings
settings = get_settings()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'etl_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'etl_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ETL_JOB_COUNT = Counter(
    'etl_jobs_total',
    'Total ETL jobs',
    ['job_type', 'status']
)

ETL_JOB_DURATION = Histogram(
    'etl_job_duration_seconds',
    'ETL job duration in seconds',
    ['job_type']
)

DATA_PROCESSED = Counter(
    'etl_data_processed_total',
    'Total data records processed',
    ['job_type', 'data_source']
)

DATA_QUALITY_SCORE = Gauge(
    'etl_data_quality_score',
    'Data quality score (0-100)',
    ['metric_type', 'data_source']
)

ACTIVE_JOBS = Gauge(
    'etl_active_jobs',
    'Number of currently active ETL jobs',
    ['job_type']
)

QUEUE_SIZE = Gauge(
    'etl_queue_size',
    'Number of jobs in queue',
    ['priority']
)

DATABASE_CONNECTIONS = Gauge(
    'etl_database_connections',
    'Number of active database connections'
)

REDIS_CONNECTIONS = Gauge(
    'etl_redis_connections',
    'Number of active Redis connections'
)

# Performance summaries
ETL_PIPELINE_DURATION = Summary(
    'etl_pipeline_duration_seconds',
    'ETL pipeline duration in seconds',
    ['pipeline_name']
)

DATA_TRANSFORMATION_DURATION = Summary(
    'etl_data_transformation_duration_seconds',
    'Data transformation duration in seconds',
    ['transformation_type']
)


def setup_monitoring():
    """Setup monitoring and observability."""
    
    # Setup OpenTelemetry if enabled
    if settings.monitoring.enabled:
        setup_tracing()
    
    # Setup Prometheus metrics if enabled
    if settings.monitoring.enabled:
        setup_prometheus()
    
    print("✅ Monitoring initialized successfully")


def setup_tracing():
    """Setup OpenTelemetry tracing."""
    try:
        # Create tracer provider
        trace.set_tracer_provider(TracerProvider())
        
        # Add console exporter for development
        if settings.is_development:
            console_exporter = ConsoleSpanExporter()
            span_processor = BatchSpanProcessor(console_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Create tracer
        tracer = trace.get_tracer(__name__)
        
        # Setup FastAPI instrumentation
        FastAPIInstrumentor().instrument()
        
        # Setup SQLAlchemy instrumentation
        SQLAlchemyInstrumentor().instrument()
        
        # Setup Redis instrumentation
        RedisInstrumentor().instrument()
        
        # Setup Requests instrumentation
        RequestsInstrumentor().instrument()
        
        print("✅ OpenTelemetry tracing initialized")
        
    except Exception as e:
        print(f"⚠️ OpenTelemetry tracing setup failed: {e}")


def setup_prometheus():
    """Setup Prometheus metrics."""
    try:
        # Initialize metrics
        REQUEST_COUNT._value._value = 0
        ETL_JOB_COUNT._value._value = 0
        DATA_PROCESSED._value._value = 0
        
        print("✅ Prometheus metrics initialized")
        
    except Exception as e:
        print(f"⚠️ Prometheus metrics setup failed: {e}")


# Metrics recording functions
def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request metrics."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


def record_etl_job(job_type: str, status: str, duration: float = None):
    """Record ETL job metrics."""
    ETL_JOB_COUNT.labels(job_type=job_type, status=status).inc()
    
    if duration:
        ETL_JOB_DURATION.labels(job_type=job_type).observe(duration)
    
    # Update active jobs count
    if status == "running":
        ACTIVE_JOBS.labels(job_type=job_type).inc()
    elif status in ["completed", "failed", "cancelled"]:
        ACTIVE_JOBS.labels(job_type=job_type).dec()


def record_data_processed(job_type: str, data_source: str, count: int):
    """Record data processing metrics."""
    DATA_PROCESSED.labels(job_type=job_type, data_source=data_source).inc(count)


def record_data_quality(metric_type: str, data_source: str, score: float):
    """Record data quality metrics."""
    DATA_QUALITY_SCORE.labels(metric_type=metric_type, data_source=data_source).set(score)


def record_queue_size(priority: str, size: int):
    """Record queue size metrics."""
    QUEUE_SIZE.labels(priority=priority).set(size)


def record_database_connections(count: int):
    """Record database connection metrics."""
    DATABASE_CONNECTIONS.set(count)


def record_redis_connections(count: int):
    """Record Redis connection metrics."""
    REDIS_CONNECTIONS.set(count)


def record_pipeline_duration(pipeline_name: str, duration: float):
    """Record ETL pipeline duration."""
    ETL_PIPELINE_DURATION.labels(pipeline_name=pipeline_name).observe(duration)


def record_transformation_duration(transformation_type: str, duration: float):
    """Record data transformation duration."""
    DATA_TRANSFORMATION_DURATION.labels(transformation_type=transformation_type).observe(duration)


# Context managers for timing operations
class MetricsTimer:
    """Context manager for timing operations and recording metrics."""
    
    def __init__(self, operation: str, labels: Dict[str, str] = None):
        self.operation = operation
        self.labels = labels or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            
            # Record metrics based on operation type
            if self.operation.startswith("etl_job"):
                record_etl_job(self.labels.get("job_type", "unknown"), "completed", duration)
            elif self.operation.startswith("pipeline"):
                record_pipeline_duration(self.labels.get("pipeline_name", "unknown"), duration)
            elif self.operation.startswith("transformation"):
                record_transformation_duration(self.labels.get("transformation_type", "unknown"), duration)
            elif self.operation.startswith("request"):
                record_request(
                    self.labels.get("method", "unknown"),
                    self.labels.get("endpoint", "unknown"),
                    self.labels.get("status", 200),
                    duration
                )


# Decorators for automatic metrics recording
def metrics_timer(operation: str, labels: Dict[str, str] = None):
    """Decorator to automatically time operations and record metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with MetricsTimer(operation, labels):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Health check metrics
def get_health_metrics() -> Dict[str, Any]:
    """Get current health metrics."""
    return {
        "active_jobs": {
            "extract": ACTIVE_JOBS.labels(job_type="extract")._value._value,
            "transform": ACTIVE_JOBS.labels(job_type="transform")._value._value,
            "load": ACTIVE_JOBS.labels(job_type="load")._value._value,
            "full_pipeline": ACTIVE_JOBS.labels(job_type="full_pipeline")._value._value
        },
        "queue_sizes": {
            "low": QUEUE_SIZE.labels(priority="low")._value._value,
            "normal": QUEUE_SIZE.labels(priority="normal")._value._value,
            "high": QUEUE_SIZE.labels(priority="high")._value._value,
            "urgent": QUEUE_SIZE.labels(priority="urgent")._value._value
        },
        "connections": {
            "database": DATABASE_CONNECTIONS._value._value,
            "redis": REDIS_CONNECTIONS._value._value
        },
        "total_requests": REQUEST_COUNT._value._value,
        "total_jobs": ETL_JOB_COUNT._value._value,
        "total_data_processed": DATA_PROCESSED._value._value
    }


# Prometheus metrics endpoint
def get_prometheus_metrics():
    """Get Prometheus metrics in text format."""
    return generate_latest(), CONTENT_TYPE_LATEST


# Custom metrics for ETL operations
ETL_EXTRACTION_SUCCESS_RATE = Gauge(
    'etl_extraction_success_rate',
    'Data extraction success rate (0-100)',
    ['data_source']
)

ETL_TRANSFORMATION_SUCCESS_RATE = Gauge(
    'etl_transformation_success_rate',
    'Data transformation success rate (0-100)',
    ['transformation_type']
)

ETL_LOADING_SUCCESS_RATE = Gauge(
    'etl_loading_success_rate',
    'Data loading success rate (0-100)',
    ['target_system']
)

DATA_FRESHNESS = Gauge(
    'etl_data_freshness_hours',
    'Data freshness in hours since last update',
    ['data_source']
)

ERROR_RATE = Gauge(
    'etl_error_rate',
    'Error rate percentage (0-100)',
    ['component']
)


def record_success_rate(operation: str, component: str, rate: float):
    """Record success rate metrics."""
    if operation == "extraction":
        ETL_EXTRACTION_SUCCESS_RATE.labels(data_source=component).set(rate)
    elif operation == "transformation":
        ETL_TRANSFORMATION_SUCCESS_RATE.labels(transformation_type=component).set(rate)
    elif operation == "loading":
        ETL_LOADING_SUCCESS_RATE.labels(target_system=component).set(rate)


def record_data_freshness(data_source: str, hours_since_update: float):
    """Record data freshness metrics."""
    DATA_FRESHNESS.labels(data_source=data_source).set(hours_since_update)


def record_error_rate(component: str, rate: float):
    """Record error rate metrics."""
    ERROR_RATE.labels(component=component).set(rate)


# Performance monitoring helpers
class PerformanceMonitor:
    """Helper class for monitoring performance metrics."""
    
    @staticmethod
    def start_timer():
        """Start a performance timer."""
        return time.time()
    
    @staticmethod
    def end_timer(start_time: float) -> float:
        """End a performance timer and return duration."""
        return time.time() - start_time
    
    @staticmethod
    def record_operation(operation: str, duration: float, **labels):
        """Record operation performance."""
        if operation.startswith("etl_"):
            record_etl_job(labels.get("job_type", "unknown"), "completed", duration)
        elif operation.startswith("pipeline_"):
            record_pipeline_duration(labels.get("pipeline_name", "unknown"), duration)
        elif operation.startswith("transformation_"):
            record_transformation_duration(labels.get("transformation_type", "unknown"), duration)
    
    @staticmethod
    def monitor_function(operation: str, **labels):
        """Decorator to monitor function performance."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = PerformanceMonitor.start_timer()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = PerformanceMonitor.end_timer(start_time)
                    PerformanceMonitor.record_operation(operation, duration, **labels)
            return wrapper
        return decorator

"""
Monitoring configuration for OpenPolicy Scraper Service
"""

import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from config import Settings

# Initialize settings
settings = Settings()

# Prometheus metrics
SCRAPER_REQUESTS = Counter(
    'scraper_requests_total',
    'Total number of scraper requests',
    ['scraper_name', 'status']
)

SCRAPER_DURATION = Histogram(
    'scraper_duration_seconds',
    'Time spent scraping',
    ['scraper_name']
)

SCRAPER_DATA_COLLECTED = Counter(
    'scraper_data_collected_total',
    'Total amount of data collected',
    ['scraper_name', 'data_type']
)

SCRAPER_ERRORS = Counter(
    'scraper_errors_total',
    'Total number of scraper errors',
    ['scraper_name', 'error_type']
)

SCRAPER_ACTIVE = Gauge(
    'scraper_active',
    'Number of active scrapers',
    ['scraper_name']
)

def setup_monitoring():
    """Setup monitoring configuration"""
    if not settings.METRICS_ENABLED:
        return
    
    # Set environment variables for Prometheus
    os.environ['PROMETHEUS_MULTIPROC_DIR'] = '/tmp'
    
    print(f"Monitoring enabled on port {settings.PROMETHEUS_PORT}")

def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

def record_scraper_request(scraper_name: str, status: str):
    """Record scraper request"""
    SCRAPER_REQUESTS.labels(scraper_name=scraper_name, status=status).inc()

def record_scraper_duration(scraper_name: str, duration: float):
    """Record scraper duration"""
    SCRAPER_DURATION.labels(scraper_name=scraper_name).observe(duration)

def record_data_collected(scraper_name: str, data_type: str, amount: int = 1):
    """Record data collected"""
    SCRAPER_DATA_COLLECTED.labels(scraper_name=scraper_name, data_type=data_type).inc(amount)

def record_scraper_error(scraper_name: str, error_type: str):
    """Record scraper error"""
    SCRAPER_ERRORS.labels(scraper_name=scraper_name, error_type=error_type).inc()

def set_scraper_active(scraper_name: str, active: bool):
    """Set scraper active status"""
    SCRAPER_ACTIVE.labels(scraper_name=scraper_name).set(1 if active else 0)

"""
OpenPolicy Scraper Service

This service orchestrates all data scraping operations for the OpenPolicy platform,
including parliamentary data, civic data, and external data sources.
"""

__version__ = "1.0.0"
__author__ = "OpenPolicy Team"
__description__ = "Data scraping and collection service for OpenPolicy platform"

# Import services to make them available at the package level
from . import services

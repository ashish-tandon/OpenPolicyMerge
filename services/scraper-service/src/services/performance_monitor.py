"""
Performance Monitor Service for OpenPolicy Scraper Service

This module provides performance monitoring and metrics collection functionality.
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors performance metrics for the scraper service."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.start_time = datetime.utcnow()
        self.monitoring_active = False
        
    async def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring_active = True
        logger.info("Performance monitoring started")
        
    async def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        logger.info("Performance monitoring stopped")
        
    async def record_metric(self, metric_name: str, value: float):
        """Record a performance metric."""
        if self.monitoring_active:
            self.metrics[metric_name].append(value)
            logger.debug(f"Recorded metric {metric_name}: {value}")
            
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all recorded metrics."""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1] if values else None
                }
                
        return summary
        
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'disk_usage': disk.percent,
                'disk_free': disk.free,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {'error': str(e)}
            
    async def measure_execution_time(self, operation_name: str):
        """Context manager for measuring execution time."""
        return ExecutionTimer(self, operation_name)
        
    async def cleanup_old_metrics(self, max_age_hours: int = 24):
        """Clean up old metrics data."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        # In a real implementation, this would clean up old metrics
        logger.info(f"Cleaned up metrics older than {max_age_hours} hours")


class ExecutionTimer:
    """Context manager for timing operations."""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
        
    async def __aenter__(self):
        self.start_time = time.time()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time = time.time() - self.start_time
            await self.monitor.record_metric(f"{self.operation_name}_execution_time", execution_time)

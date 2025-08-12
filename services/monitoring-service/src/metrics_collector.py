import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest
from sqlalchemy import text
from .database import get_session
import asyncio
import json
import uuid

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Comprehensive metrics collection for OpenPolicy platform"""
    
    def __init__(self):
        # Initialize Prometheus metrics
        self._init_prometheus_metrics()
        
        # Metrics storage
        self.metrics_buffer = []
        self.buffer_size = 1000
        self.flush_interval = 60  # seconds
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        # HTTP request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'service']
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'service'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Database metrics
        self.db_connections_active = Gauge(
            'db_connections_active',
            'Active database connections',
            ['database', 'schema']
        )
        
        self.db_query_duration_seconds = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['database', 'schema', 'query_type'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
        )
        
        self.db_errors_total = Counter(
            'db_errors_total',
            'Total database errors',
            ['database', 'schema', 'error_type']
        )
        
        # Service health metrics
        self.service_health_status = Gauge(
            'service_health_status',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service_name', 'endpoint']
        )
        
        self.service_response_time_seconds = Histogram(
            'service_response_time_seconds',
            'Service response time in seconds',
            ['service_name', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )
        
        # Policy evaluation metrics
        self.policy_evaluations_total = Counter(
            'policy_evaluations_total',
            'Total policy evaluations',
            ['policy_id', 'decision', 'service']
        )
        
        self.policy_evaluation_duration_seconds = Histogram(
            'policy_evaluation_duration_seconds',
            'Policy evaluation duration in seconds',
            ['policy_id', 'service'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
        )
        
        # Search metrics
        self.search_queries_total = Counter(
            'search_queries_total',
            'Total search queries',
            ['query_type', 'service']
        )
        
        self.search_query_duration_seconds = Histogram(
            'search_query_duration_seconds',
            'Search query duration in seconds',
            ['query_type', 'service'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
        )
        
        # Authentication metrics
        self.auth_attempts_total = Counter(
            'auth_attempts_total',
            'Total authentication attempts',
            ['username', 'success', 'service']
        )
        
        self.active_sessions = Gauge(
            'active_sessions',
            'Number of active user sessions',
            ['service']
        )
        
        # Notification metrics
        self.notifications_sent_total = Counter(
            'notifications_sent_total',
            'Total notifications sent',
            ['notification_type', 'channel', 'service']
        )
        
        self.notification_delivery_duration_seconds = Histogram(
            'notification_delivery_duration_seconds',
            'Notification delivery duration in seconds',
            ['notification_type', 'channel'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # System metrics
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['service', 'type']
        )
        
        self.cpu_usage_percent = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            ['service']
        )
        
        self.disk_usage_bytes = Gauge(
            'disk_usage_bytes',
            'Disk usage in bytes',
            ['service', 'mount_point']
        )
        
        # Custom business metrics
        self.documents_processed_total = Counter(
            'documents_processed_total',
            'Total documents processed',
            ['document_type', 'status', 'service']
        )
        
        self.data_sync_duration_seconds = Histogram(
            'data_sync_duration_seconds',
            'Data synchronization duration in seconds',
            ['data_source', 'service'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
        )
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, 
                           service: str, duration: float):
        """Record HTTP request metrics"""
        try:
            self.http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                service=service
            ).inc()
            
            self.http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
                service=service
            ).observe(duration)
            
            # Store in buffer for database
            self._store_metric('http_request', {
                'method': method,
                'endpoint': endpoint,
                'status_code': status_code,
                'service': service,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to record HTTP request metrics: {e}")
    
    def record_db_operation(self, database: str, schema: str, query_type: str, 
                           duration: float, success: bool, error_type: str = None):
        """Record database operation metrics"""
        try:
            if success:
                self.db_query_duration_seconds.labels(
                    database=database,
                    schema=schema,
                    query_type=query_type
                ).observe(duration)
            else:
                self.db_errors_total.labels(
                    database=database,
                    schema=schema,
                    error_type=error_type or 'unknown'
                ).inc()
            
            # Store in buffer for database
            self._store_metric('db_operation', {
                'database': database,
                'schema': schema,
                'query_type': query_type,
                'duration': duration,
                'success': success,
                'error_type': error_type,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to record database metrics: {e}")
    
    def record_policy_evaluation(self, policy_id: str, decision: str, service: str, 
                                duration: float):
        """Record policy evaluation metrics"""
        try:
            self.policy_evaluations_total.labels(
                policy_id=policy_id,
                decision=decision,
                service=service
            ).inc()
            
            self.policy_evaluation_duration_seconds.labels(
                policy_id=policy_id,
                service=service
            ).observe(duration)
            
            # Store in buffer for database
            self._store_metric('policy_evaluation', {
                'policy_id': policy_id,
                'decision': decision,
                'service': service,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to record policy evaluation metrics: {e}")
    
    def record_search_query(self, query_type: str, service: str, duration: float):
        """Record search query metrics"""
        try:
            self.search_queries_total.labels(
                query_type=query_type,
                service=service
            ).inc()
            
            self.search_query_duration_seconds.labels(
                query_type=query_type,
                service=service
            ).observe(duration)
            
            # Store in buffer for database
            self._store_metric('search_query', {
                'query_type': query_type,
                'service': service,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to record search query metrics: {e}")
    
    def record_auth_attempt(self, username: str, success: bool, service: str):
        """Record authentication attempt metrics"""
        try:
            self.auth_attempts_total.labels(
                username=username,
                success=str(success).lower(),
                service=service
            ).inc()
            
            # Store in buffer for database
            self._store_metric('auth_attempt', {
                'username': username,
                'success': success,
                'service': service,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to record auth attempt metrics: {e}")
    
    def record_notification(self, notification_type: str, channel: str, service: str, 
                           duration: float):
        """Record notification metrics"""
        try:
            self.notifications_sent_total.labels(
                notification_type=notification_type,
                channel=channel,
                service=service
            ).inc()
            
            self.notification_delivery_duration_seconds.labels(
                notification_type=notification_type,
                channel=channel
            ).observe(duration)
            
            # Store in buffer for database
            self._store_metric('notification', {
                'notification_type': notification_type,
                'channel': channel,
                'service': service,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to record notification metrics: {e}")
    
    def update_service_health(self, service_name: str, endpoint: str, healthy: bool):
        """Update service health status"""
        try:
            self.service_health_status.labels(
                service_name=service_name,
                endpoint=endpoint
            ).set(1 if healthy else 0)
            
        except Exception as e:
            logger.error(f"Failed to update service health: {e}")
    
    def update_system_metrics(self, service: str, memory_bytes: int, cpu_percent: float, 
                             disk_bytes: int, mount_point: str = "/"):
        """Update system resource metrics"""
        try:
            self.memory_usage_bytes.labels(
                service=service,
                type='rss'
            ).set(memory_bytes)
            
            self.cpu_usage_percent.labels(
                service=service
            ).set(cpu_percent)
            
            self.disk_usage_bytes.labels(
                service=service,
                mount_point=mount_point
            ).set(disk_bytes)
            
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")
    
    def record_business_metric(self, metric_name: str, value: float, labels: Dict[str, str]):
        """Record custom business metrics"""
        try:
            # Store in buffer for database
            self._store_metric('business_metric', {
                'metric_name': metric_name,
                'value': value,
                'labels': labels,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to record business metric: {e}")
    
    def _store_metric(self, metric_type: str, data: Dict[str, Any]):
        """Store metric in buffer for database persistence"""
        try:
            metric_data = {
                'id': str(uuid.uuid4()),
                'metric_type': metric_type,
                'data': json.dumps(data),
                'created_at': datetime.now()
            }
            
            self.metrics_buffer.append(metric_data)
            
            # Flush if buffer is full
            if len(self.metrics_buffer) >= self.buffer_size:
                asyncio.create_task(self._flush_metrics())
                
        except Exception as e:
            logger.error(f"Failed to store metric in buffer: {e}")
    
    async def _flush_metrics(self):
        """Flush metrics from buffer to database"""
        if not self.metrics_buffer:
            return
        
        try:
            session = get_session()
            
            # Batch insert metrics
            for metric_data in self.metrics_buffer:
                session.execute(
                    text("""
                        INSERT INTO monitoring.metrics 
                        (id, metric_type, data, created_at)
                        VALUES (:id, :metric_type, :data, :created_at)
                    """),
                    metric_data
                )
            
            session.commit()
            
            # Clear buffer
            self.metrics_buffer.clear()
            
            logger.info(f"Flushed {len(self.metrics_buffer)} metrics to database")
            
        except Exception as e:
            logger.error(f"Failed to flush metrics to database: {e}")
    
    async def start_periodic_flush(self):
        """Start periodic metric flushing"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_metrics()
            except Exception as e:
                logger.error(f"Periodic flush error: {e}")
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        try:
            return generate_latest()
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return ""
    
    async def get_metrics_summary(self, time_range: str = "1h") -> Dict[str, Any]:
        """Get metrics summary for specified time range"""
        try:
            session = get_session()
            
            # Calculate time range
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # Get metrics summary
            result = session.execute(
                text("""
                    SELECT 
                        metric_type,
                        COUNT(*) as count,
                        AVG(CAST(data->>'duration' AS FLOAT)) as avg_duration,
                        MAX(CAST(data->>'duration' AS FLOAT)) as max_duration,
                        MIN(CAST(data->>'duration' AS FLOAT)) as min_duration
                    FROM monitoring.metrics 
                    WHERE created_at BETWEEN :start_time AND :end_time
                    GROUP BY metric_type
                """),
                {"start_time": start_time, "end_time": end_time}
            ).fetchall()
            
            summary = {}
            for row in result:
                summary[row[0]] = {
                    'count': row[1],
                    'avg_duration': row[2],
                    'max_duration': row[3],
                    'min_duration': row[4]
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}
    
    async def cleanup_old_metrics(self, days_to_keep: int = 30):
        """Clean up old metrics from database"""
        try:
            session = get_session()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            result = session.execute(
                text("""
                    DELETE FROM monitoring.metrics 
                    WHERE created_at < :cutoff_date
                """),
                {"cutoff_date": cutoff_date}
            )
            
            session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} old metrics")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
            return 0

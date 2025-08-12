"""
Celery Application for ETL Service

Configures Celery for background task processing including data extraction,
transformation, loading, and chart generation.
"""

from celery import Celery
from config import settings
import os

# Create Celery instance
celery_app = Celery(
    "etl_service",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=[
        "tasks.data_extraction",
        "tasks.data_transformation", 
        "tasks.data_loading",
        "tasks.chart_generation",
        "tasks.notifications"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "tasks.data_extraction.*": {"queue": "extraction"},
        "tasks.data_transformation.*": {"queue": "transformation"},
        "tasks.data_loading.*": {"queue": "loading"},
        "tasks.chart_generation.*": {"queue": "charts"},
        "tasks.notifications.*": {"queue": "notifications"}
    },
    
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Task execution limits
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
    worker_max_memory_per_child=200000,  # 200MB
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "extract-parliamentary-data": {
            "task": "tasks.data_extraction.extract_parliamentary_data",
            "schedule": 3600.0,  # Every hour
            "args": (),
            "options": {"queue": "extraction"}
        },
        "extract-civic-data": {
            "task": "tasks.data_extraction.extract_civic_data", 
            "schedule": 7200.0,  # Every 2 hours
            "args": (),
            "options": {"queue": "extraction"}
        },
        "update-data-quality-metrics": {
            "task": "tasks.data_transformation.update_data_quality_metrics",
            "schedule": 1800.0,  # Every 30 minutes
            "args": (),
            "options": {"queue": "transformation"}
        },
        "generate-daily-reports": {
            "task": "tasks.chart_generation.generate_daily_reports",
            "schedule": 86400.0,  # Daily at midnight
            "args": (),
            "options": {"queue": "charts"}
        },
        "cleanup-old-data": {
            "task": "tasks.data_loading.cleanup_old_data",
            "schedule": 604800.0,  # Weekly
            "args": (),
            "options": {"queue": "loading"}
        }
    },
    
    # Task routing by priority
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Security
    security_key=settings.celery.security_key,
    security_certificate=settings.celery.security_certificate,
    security_cert_store=settings.celery.security_cert_store,
    
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s"
)

# Task routing by priority
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    print(f"Request: {self.request!r}")
    return "Debug task completed successfully"

# Health check task
@celery_app.task(bind=True)
def health_check(self):
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "worker_id": self.request.id,
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Task monitoring
@celery_app.task(bind=True)
def monitor_task_progress(self, task_id):
    """Monitor progress of a specific task"""
    task_result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
        "info": task_result.info
    }

# Error handling
@celery_app.task(bind=True)
def handle_task_failure(self, task_id, error_message):
    """Handle task failures and send notifications"""
    # Log the failure
    self.logger.error(f"Task {task_id} failed: {error_message}")
    
    # Send notification (if configured)
    try:
        from tasks.notifications import send_task_failure_notification
        send_task_failure_notification.delay(task_id, error_message)
    except Exception as e:
        self.logger.error(f"Failed to send failure notification: {e}")
    
    return {
        "task_id": task_id,
        "status": "failed",
        "error": error_message,
        "handled_at": "2024-01-01T00:00:00Z"
    }

# Task cleanup
@celery_app.task(bind=True)
def cleanup_completed_tasks(self, older_than_hours=24):
    """Clean up completed tasks older than specified hours"""
    try:
        from datetime import datetime, timedelta
        from database import get_db
        from models.etl_job import ETLJob
        
        db = next(get_db())
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        # Clean up old completed jobs
        old_jobs = db.query(ETLJob).filter(
            ETLJob.status.in_(["completed", "failed"]),
            ETLJob.updated_at < cutoff_time
        ).all()
        
        for job in old_jobs:
            job.is_active = False
            job.deleted_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "cleaned_jobs": len(old_jobs),
            "cutoff_time": cutoff_time.isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        self.logger.error(f"Failed to cleanup tasks: {e}")
        return {
            "error": str(e),
            "status": "failed"
        }

# Export the Celery app
__all__ = ["celery_app"]

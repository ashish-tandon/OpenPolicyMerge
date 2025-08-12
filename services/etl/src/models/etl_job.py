"""
ETL Job model for tracking data processing jobs.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from .base import Base


class JobStatus(enum.Enum):
    """ETL job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class JobType(enum.Enum):
    """ETL job type enumeration."""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    FULL_PIPELINE = "full_pipeline"
    VALIDATION = "validation"
    CLEANUP = "cleanup"


class JobPriority(enum.Enum):
    """ETL job priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ETLJob(Base):
    """ETL Job model for tracking data processing jobs."""
    
    __tablename__ = "etl_jobs"
    
    # Job identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    job_type = Column(Enum(JobType), nullable=False, index=True)
    priority = Column(Enum(JobPriority), default=JobPriority.NORMAL, index=True)
    
    # Status and progress
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    progress = Column(Integer, default=0)  # 0-100 percentage
    current_step = Column(String(255), nullable=True)
    total_steps = Column(Integer, default=1)
    
    # Timing
    scheduled_at = Column(DateTime, nullable=True, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    
    # Performance metrics
    records_processed = Column(Integer, default=0)
    records_total = Column(Integer, default=0)
    processing_time = Column(Integer, default=0)  # seconds
    memory_usage = Column(Integer, default=0)  # MB
    cpu_usage = Column(Float, default=0.0)  # percentage
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_retry_at = Column(DateTime, nullable=True)
    
    # Configuration and data
    config = Column(JSON, nullable=True)  # Job configuration
    input_data = Column(JSON, nullable=True)  # Input data specification
    output_data = Column(JSON, nullable=True)  # Output data specification
    dependencies = Column(JSON, nullable=True)  # Job dependencies
    
    # Relationships
    data_source_id = Column(String(36), ForeignKey("datasources.id"), nullable=True)
    schedule_id = Column(String(36), ForeignKey("schedules.id"), nullable=True)
    parent_job_id = Column(String(36), ForeignKey("etl_jobs.id"), nullable=True)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="etl_jobs")
    schedule = relationship("Schedule", back_populates="etl_jobs")
    parent_job = relationship("ETLJob", remote_side=[id], backref="child_jobs")
    processing_logs = relationship("ProcessingLog", back_populates="etl_job")
    
    def __init__(self, **kwargs):
        """Initialize ETL Job with UUID."""
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    @property
    def duration(self) -> Optional[int]:
        """Get job duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        elif self.started_at:
            return int((datetime.utcnow() - self.started_at).total_seconds())
        return None
    
    @property
    def is_running(self) -> bool:
        """Check if job is currently running."""
        return self.status == JobStatus.RUNNING
    
    @property
    def is_completed(self) -> bool:
        """Check if job is completed."""
        return self.status == JobStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if job has failed."""
        return self.status == JobStatus.FAILED
    
    @property
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.status == JobStatus.FAILED and self.retry_count < self.max_retries
    
    @property
    def is_overdue(self) -> bool:
        """Check if job is overdue."""
        if self.scheduled_at and self.status == JobStatus.PENDING:
            return datetime.utcnow() > self.scheduled_at
        return False
    
    def start(self) -> None:
        """Start the job."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.progress = 0
    
    def complete(self, **kwargs) -> None:
        """Complete the job."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 100
        
        # Update metrics
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def fail(self, error_message: str) -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
    
    def pause(self) -> None:
        """Pause the job."""
        if self.status == JobStatus.RUNNING:
            self.status = JobStatus.PAUSED
    
    def resume(self) -> None:
        """Resume a paused job."""
        if self.status == JobStatus.PAUSED:
            self.status = JobStatus.RUNNING
    
    def cancel(self) -> None:
        """Cancel the job."""
        if self.status in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.PAUSED]:
            self.status = JobStatus.CANCELLED
            self.completed_at = datetime.utcnow()
    
    def retry(self) -> None:
        """Retry a failed job."""
        if self.can_retry:
            self.status = JobStatus.PENDING
            self.retry_count += 1
            self.last_retry_at = datetime.utcnow()
            self.error_message = None
            self.progress = 0
            self.started_at = None
            self.completed_at = None
    
    def update_progress(self, progress: int, current_step: str = None) -> None:
        """Update job progress."""
        self.progress = max(0, min(100, progress))
        if current_step:
            self.current_step = current_step
        self.updated_at = datetime.utcnow()
    
    def add_metrics(self, records_processed: int = None, memory_usage: int = None, 
                   cpu_usage: float = None) -> None:
        """Add performance metrics."""
        if records_processed is not None:
            self.records_processed = records_processed
        if memory_usage is not None:
            self.memory_usage = memory_usage
        if cpu_usage is not None:
            self.cpu_usage = cpu_usage
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with additional properties."""
        result = super().to_dict()
        result.update({
            'duration': self.duration,
            'is_running': self.is_running,
            'is_completed': self.is_completed,
            'is_failed': self.is_failed,
            'can_retry': self.can_retry,
            'is_overdue': self.is_overdue
        })
        return result
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<ETLJob(id={self.id}, name='{self.name}', status={self.status.value})>"

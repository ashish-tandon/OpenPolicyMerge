"""
Processing Log model for tracking ETL processing activities.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base


class ProcessingLog(Base):
    """Log of ETL processing activities."""
    
    __tablename__ = "processing_logs"
    
    # Fields
    etl_job_id = Column(String(36), ForeignKey("etljobs.id"), nullable=False, index=True)
    step_name = Column(String(255), nullable=False)
    step_order = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="started")  # started, completed, failed
    message = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    records_processed = Column(Integer, nullable=True)
    records_failed = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)  # Additional processing metadata
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    etl_job = relationship("ETLJob", back_populates="processing_logs")
    
    def __init__(self, **kwargs):
        """Initialize Processing Log."""
        super().__init__(**kwargs)
        if 'id' not in kwargs:
            from uuid import uuid4
            kwargs['id'] = str(uuid4())
    
    def start_step(self, step_name: str, step_order: int, **kwargs):
        """Start a processing step."""
        self.step_name = step_name
        self.step_order = step_order
        self.status = "started"
        self.started_at = datetime.utcnow()
        self.metadata_json = kwargs.get('metadata', {})
    
    def complete_step(self, **kwargs):
        """Complete a processing step."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        
        # Calculate duration
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def fail_step(self, error_message: str, error_details: str = None, **kwargs):
        """Mark a processing step as failed."""
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        self.error_details = error_details
        
        # Calculate duration
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def is_completed(self) -> bool:
        """Check if step is completed."""
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """Check if step failed."""
        return self.status == "failed"
    
    @property
    def is_running(self) -> bool:
        """Check if step is running."""
        return self.status == "started"
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration string."""
        if not self.duration_seconds:
            return "N/A"
        
        if self.duration_seconds < 60:
            return f"{self.duration_seconds}s"
        elif self.duration_seconds < 3600:
            minutes = self.duration_seconds // 60
            seconds = self.duration_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = self.duration_seconds // 3600
            minutes = (self.duration_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = super().to_dict()
        result['duration_formatted'] = self.duration_formatted
        return result
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<ProcessingLog(id={self.id}, step={self.step_name}, status={self.status})>"

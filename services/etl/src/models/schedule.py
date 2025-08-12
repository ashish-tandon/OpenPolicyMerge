"""
Schedule model for ETL job scheduling.
"""
from datetime import datetime, time
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, ForeignKey, Time, JSON
from sqlalchemy.orm import relationship

from .base import Base


class Schedule(Base):
    """Schedule for ETL jobs."""
    
    __tablename__ = "schedules"
    
    # Fields
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cron_expression = Column(String(100), nullable=True)  # Cron expression for scheduling
    time_zone = Column(String(50), nullable=False, default="UTC")
    
    # Time-based scheduling
    start_time = Column(Time, nullable=True)  # Daily start time
    end_time = Column(Time, nullable=True)    # Daily end time
    days_of_week = Column(String(50), nullable=True)  # Comma-separated days (1=Monday, 7=Sunday)
    days_of_month = Column(String(100), nullable=True)  # Comma-separated days or "L" for last day
    
    # Frequency
    frequency = Column(String(50), nullable=False, default="daily")  # daily, weekly, monthly, custom
    interval = Column(Integer, nullable=False, default=1)  # Every N days/weeks/months
    
    # Status and control
    is_active = Column(Boolean, default=True, nullable=False)
    is_paused = Column(Boolean, default=False, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    retry_delay_minutes = Column(Integer, default=15, nullable=False)
    
    # Next run tracking
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    total_runs = Column(Integer, default=0, nullable=False)
    successful_runs = Column(Integer, default=0, nullable=False)
    failed_runs = Column(Integer, default=0, nullable=False)
    
    # Configuration
    config = Column(JSON, nullable=True)  # Additional schedule configuration
    metadata_json = Column(JSON, nullable=True)  # Additional metadata
    
    # Relationships
    etl_jobs = relationship("ETLJob", back_populates="schedule")
    
    def __init__(self, **kwargs):
        """Initialize Schedule."""
        super().__init__(**kwargs)
        if 'id' not in kwargs:
            from uuid import uuid4
            kwargs['id'] = str(uuid4())
    
    @property
    def is_enabled(self) -> bool:
        """Check if schedule is enabled."""
        return self.is_active and not self.is_paused
    
    @property
    def status(self) -> str:
        """Get schedule status."""
        if not self.is_active:
            return "disabled"
        elif self.is_paused:
            return "paused"
        elif self.next_run_at and self.next_run_at < datetime.utcnow():
            return "overdue"
        else:
            return "active"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100
    
    def calculate_next_run(self) -> Optional[datetime]:
        """Calculate the next run time based on schedule."""
        if not self.is_enabled:
            return None
        
        now = datetime.utcnow()
        
        if self.cron_expression:
            # Use cron expression for next run
            try:
                from croniter import croniter
                cron = croniter(self.cron_expression, now)
                return cron.get_next(datetime)
            except ImportError:
                # Fallback to basic calculation
                pass
        
        # Basic time-based calculation
        if self.frequency == "daily":
            if self.start_time:
                next_run = datetime.combine(now.date(), self.start_time)
                if next_run <= now:
                    next_run = next_run.replace(day=next_run.day + self.interval)
                return next_run
        
        elif self.frequency == "weekly":
            if self.start_time:
                # Find next occurrence of start_time
                next_run = datetime.combine(now.date(), self.start_time)
                days_ahead = (self.interval * 7) - (now.weekday() - 0) % (self.interval * 7)
                next_run = next_run.replace(day=next_run.day + days_ahead)
                return next_run
        
        elif self.frequency == "monthly":
            if self.start_time:
                # Find next occurrence of start_time in next month
                next_run = datetime.combine(now.date(), self.start_time)
                if next_run <= now:
                    # Move to next month
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
                return next_run
        
        return None
    
    def update_run_stats(self, success: bool) -> None:
        """Update run statistics."""
        self.last_run_at = datetime.utcnow()
        self.total_runs += 1
        
        if success:
            self.successful_runs += 1
        else:
            self.failed_runs += 1
        
        # Calculate next run
        self.next_run_at = self.calculate_next_run()
    
    def pause(self) -> None:
        """Pause the schedule."""
        self.is_paused = True
    
    def resume(self) -> None:
        """Resume the schedule."""
        self.is_paused = False
        self.next_run_at = self.calculate_next_run()
    
    def disable(self) -> None:
        """Disable the schedule."""
        self.is_active = False
        self.is_paused = False
    
    def enable(self) -> None:
        """Enable the schedule."""
        self.is_active = True
        self.is_paused = False
        self.next_run_at = self.calculate_next_run()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = super().to_dict()
        result['status'] = self.status
        result['success_rate'] = self.success_rate
        result['is_enabled'] = self.is_enabled
        return result
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Schedule(id={self.id}, name={self.name}, status={self.status})>"

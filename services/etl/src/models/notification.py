"""
Notification model for ETL system notifications.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base


class Notification(Base):
    """Notification for ETL system events."""
    
    __tablename__ = "notifications"
    
    # Fields
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default="info")  # info, warning, error, success
    priority = Column(String(20), nullable=False, default="normal")  # low, normal, high, critical
    
    # Source and context
    source_service = Column(String(100), nullable=False, default="etl")  # etl, scraper, api, etc.
    source_id = Column(String(36), nullable=True)  # ID of the source object (job, schedule, etc.)
    context = Column(JSON, nullable=True)  # Additional context data
    
    # Status and delivery
    is_read = Column(Boolean, default=False, nullable=False)
    is_delivered = Column(Boolean, default=False, nullable=False)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Recipients and channels
    recipient_type = Column(String(50), nullable=False, default="system")  # system, user, admin, all
    recipient_id = Column(String(36), nullable=True)  # User ID if recipient_type is user
    channels = Column(JSON, nullable=True)  # List of delivery channels: email, webhook, slack, etc.
    
    # Expiration and retry
    expires_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # List of tags for categorization
    metadata_json = Column(JSON, nullable=True)  # Additional metadata
    
    def __init__(self, **kwargs):
        """Initialize Notification."""
        super().__init__(**kwargs)
        if 'id' not in kwargs:
            from uuid import uuid4
            kwargs['id'] = str(uuid4())
    
    @property
    def is_expired(self) -> bool:
        """Check if notification is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @property
    def is_actionable(self) -> bool:
        """Check if notification requires action."""
        return not self.is_read and not self.is_expired
    
    @property
    def age_hours(self) -> float:
        """Get notification age in hours."""
        if self.created_at:
            delta = datetime.utcnow() - self.created_at
            return delta.total_seconds() / 3600
        return 0.0
    
    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def mark_as_unread(self) -> None:
        """Mark notification as unread."""
        self.is_read = False
        self.read_at = None
    
    def mark_as_delivered(self) -> None:
        """Mark notification as delivered."""
        self.is_delivered = True
        self.delivered_at = datetime.utcnow()
    
    def retry_delivery(self) -> bool:
        """Retry delivery if possible."""
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.is_delivered = False
            self.delivered_at = None
            return True
        return False
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the notification."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the notification."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
    
    def add_context(self, key: str, value: Any) -> None:
        """Add context data to the notification."""
        if not self.context:
            self.context = {}
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context data from the notification."""
        if self.context:
            return self.context.get(key, default)
        return default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = super().to_dict()
        result['is_expired'] = self.is_expired
        result['is_actionable'] = self.is_actionable
        result['age_hours'] = self.age_hours
        return result
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Notification(id={self.id}, type={self.notification_type}, title={self.title})>"

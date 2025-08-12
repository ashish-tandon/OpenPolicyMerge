from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'schema': 'notifications'}

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default='info')  # info, warning, error, success
    priority = Column(String(20), default='normal')  # low, normal, high, urgent
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    metadata = Column(JSON)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NotificationTemplate(Base):
    __tablename__ = 'notification_templates'
    __table_args__ = {'schema': 'notifications'}

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False)
    title_template = Column(String(500), nullable=False)
    message_template = Column(Text, nullable=False)
    notification_type = Column(String(50), default='info')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NotificationPreference(Base):
    __tablename__ = 'notification_preferences'
    __table_args__ = {'schema': 'notifications'}

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False)
    notification_type = Column(String(50), nullable=False)
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

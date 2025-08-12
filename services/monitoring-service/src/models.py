from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class ServiceHealth(Base):
    __tablename__ = 'service_health'
    __table_args__ = {'schema': 'monitoring'}

    id = Column(String, primary_key=True, default=generate_uuid)
    service_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # healthy, unhealthy, degraded
    response_time_ms = Column(Integer)
    last_check = Column(DateTime(timezone=True), nullable=False)
    error_message = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Metric(Base):
    __tablename__ = 'metrics'
    __table_args__ = {'schema': 'monitoring'}

    id = Column(String, primary_key=True, default=generate_uuid)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50))  # counter, gauge, histogram
    service_name = Column(String(100))
    labels = Column(JSON)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = 'alerts'
    __table_args__ = {'schema': 'monitoring'}

    id = Column(String, primary_key=True, default=generate_uuid)
    alert_name = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    status = Column(String(50), default='firing')  # firing, resolved
    description = Column(Text)
    service_name = Column(String(100))
    metric_name = Column(String(255))
    threshold_value = Column(Float)
    current_value = Column(Float)
    fired_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LogEntry(Base):
    __tablename__ = 'log_entries'
    __table_args__ = {'schema': 'monitoring'}

    id = Column(String, primary_key=True, default=generate_uuid)
    service_name = Column(String(100), nullable=False)
    level = Column(String(20), nullable=False)  # debug, info, warning, error, critical
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    trace_id = Column(String(100))
    user_id = Column(String(100))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

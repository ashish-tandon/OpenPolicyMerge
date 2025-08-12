from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Configuration(Base):
    __tablename__ = 'configurations'
    __table_args__ = {'schema': 'config'}

    id = Column(String, primary_key=True, default=generate_uuid)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    value_type = Column(String(50), default='string')  # string, integer, boolean, json
    description = Column(Text)
    category = Column(String(100))
    is_encrypted = Column(Boolean, default=False)
    is_sensitive = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(100))

class ConfigurationAudit(Base):
    __tablename__ = 'configuration_audit'
    __table_args__ = {'schema': 'config'}

    id = Column(String, primary_key=True, default=generate_uuid)
    config_key = Column(String(255), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    change_type = Column(String(50))  # create, update, delete
    changed_by = Column(String(100))
    change_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ConfigurationEnvironment(Base):
    __tablename__ = 'configuration_environments'
    __table_args__ = {'schema': 'config'}

    id = Column(String, primary_key=True, default=generate_uuid)
    environment = Column(String(100), nullable=False)  # dev, staging, prod
    config_key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    is_override = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

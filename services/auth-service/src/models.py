from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    roles = relationship("UserRole", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")

class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'auth'}

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserRole(Base):
    __tablename__ = 'user_roles'
    __table_args__ = {'schema': 'auth'}

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('auth.users.id'), nullable=False)
    role_id = Column(String, ForeignKey('auth.roles.id'), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role")

class UserSession(Base):
    __tablename__ = 'user_sessions'
    __table_args__ = {'schema': 'auth'}

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('auth.users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")

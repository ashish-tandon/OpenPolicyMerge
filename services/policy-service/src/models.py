from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Policy(Base):
    __tablename__ = 'policies'
    __table_args__ = {'schema': 'policy'}

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    version = Column(String(50), default='1.0.0')
    status = Column(String(50), default='draft')  # draft, active, deprecated
    category = Column(String(100))
    tags = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100))
    
    # Relationships
    evaluations = relationship("PolicyEvaluation", back_populates="policy")

class PolicyEvaluation(Base):
    __tablename__ = 'policy_evaluations'
    __table_args__ = {'schema': 'policy'}

    id = Column(String, primary_key=True, default=generate_uuid)
    policy_id = Column(String, ForeignKey('policy.policies.id'), nullable=False)
    input_data = Column(JSON, nullable=False)
    result = Column(JSON, nullable=False)
    decision = Column(String(50), nullable=False)  # allow, deny, unknown
    confidence = Column(Integer)  # 0-100
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    policy = relationship("Policy", back_populates="evaluations")

class PolicyRule(Base):
    __tablename__ = 'policy_rules'
    __table_args__ = {'schema': 'policy'}

    id = Column(String, primary_key=True, default=generate_uuid)
    policy_id = Column(String, ForeignKey('policy.policies.id'), nullable=False)
    rule_name = Column(String(255), nullable=False)
    rule_content = Column(Text, nullable=False)
    priority = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PolicyBundle(Base):
    __tablename__ = 'policy_bundles'
    __table_args__ = {'schema': 'policy'}

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), default='1.0.0')
    policies = Column(JSON)  # Array of policy IDs
    status = Column(String(50), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

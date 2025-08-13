from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class SearchIndex(Base):
    __tablename__ = 'search_indices'
    __table_args__ = {'schema': 'search'}

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, nullable=False)
    document_type = Column(String(100), nullable=False)  # policy, bill, representative, etc.
    title = Column(String(500))
    content = Column(Text)
    summary = Column(Text)
    document_metadata = Column(JSON)
    search_vector = Column(Text)  # Full-text search vector
    relevance_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    indexed_at = Column(DateTime(timezone=True))

class SearchQuery(Base):
    __tablename__ = 'search_queries'
    __table_args__ = {'schema': 'search'}

    id = Column(String, primary_key=True, default=generate_uuid)
    query_text = Column(Text, nullable=False)
    user_id = Column(String(100))
    filters = Column(JSON)
    results_count = Column(Integer, default=0)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SearchSuggestion(Base):
    __tablename__ = 'search_suggestions'
    __table_args__ = {'schema': 'search'}

    id = Column(String, primary_key=True, default=generate_uuid)
    suggestion_text = Column(String(500), nullable=False)
    suggestion_type = Column(String(50))  # autocomplete, related, popular
    frequency = Column(Integer, default=1)
    last_used = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/openpolicy')

def get_engine():
    """Get database engine with connection pooling"""
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

def get_session():
    """Get database session"""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def init_database():
    """Initialize database with required schemas and tables"""
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # Create search schema if it doesn't exist
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS search"))
            conn.commit()
            
            # Create tables
            create_search_tables(conn)
            conn.commit()
            
        print("Search database initialized successfully")
        return True
        
    except SQLAlchemyError as e:
        print(f"Search database initialization failed: {e}")
        return False

def create_search_tables(conn):
    """Create search service tables"""
    
    # Search indices table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS search.search_indices (
            id VARCHAR PRIMARY KEY,
            document_id VARCHAR NOT NULL,
            document_type VARCHAR(100) NOT NULL,
            title VARCHAR(500),
            content TEXT,
            summary TEXT,
            metadata JSONB,
            search_vector TSVECTOR,
            relevance_score FLOAT DEFAULT 0.0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            indexed_at TIMESTAMP WITH TIME ZONE
        )
    """))
    
    # Search queries table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS search.search_queries (
            id VARCHAR PRIMARY KEY,
            query_text TEXT NOT NULL,
            user_id VARCHAR(100),
            filters JSONB,
            results_count INTEGER DEFAULT 0,
            execution_time_ms INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))
    
    # Search suggestions table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS search.search_suggestions (
            id VARCHAR PRIMARY KEY,
            suggestion_text VARCHAR(500) NOT NULL,
            suggestion_type VARCHAR(50),
            frequency INTEGER DEFAULT 1,
            last_used TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))
    
    # Create indexes and full-text search
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_search_document_type ON search.search_indices(document_type)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_search_relevance ON search.search_indices(relevance_score)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_search_vector ON search.search_indices USING GIN(search_vector)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_suggestions_type ON search.search_suggestions(suggestion_type)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_suggestions_frequency ON search.search_suggestions(frequency)"))

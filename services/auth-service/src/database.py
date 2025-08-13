import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

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
            # Create policy schema if it doesn't exist
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS policy"))
            conn.commit()
            
            # Create tables
            create_policy_tables(conn)
            conn.commit()
            
        print("Database initialized successfully")
        return True
        
    except SQLAlchemyError as e:
        print(f"Database initialization failed: {e}")
        return False

def create_policy_tables(conn):
    """Create policy service tables"""
    
    # Policies table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS policy.policies (
            id VARCHAR PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            version VARCHAR(50) DEFAULT '1.0.0',
            status VARCHAR(50) DEFAULT 'draft',
            category VARCHAR(100),
            tags JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by VARCHAR(100)
        )
    """))
    
    # Policy evaluations table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS policy.policy_evaluations (
            id VARCHAR PRIMARY KEY,
            policy_id VARCHAR NOT NULL,
            input_data JSONB NOT NULL,
            result JSONB NOT NULL,
            decision VARCHAR(50) NOT NULL,
            confidence INTEGER,
            execution_time_ms INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (policy_id) REFERENCES policy.policies(id)
        )
    """))
    
    # Policy rules table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS policy.policy_rules (
            id VARCHAR PRIMARY KEY,
            policy_id VARCHAR NOT NULL,
            rule_name VARCHAR(255) NOT NULL,
            rule_content TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (policy_id) REFERENCES policy.policies(id)
        )
    """))
    
    # Policy bundles table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS policy.policy_bundles (
            id VARCHAR PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            version VARCHAR(50) DEFAULT '1.0.0',
            policies JSONB,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))
    
    # Create indexes
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_policies_status ON policy.policies(status)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_policies_category ON policy.policies(category)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_evaluations_policy_id ON policy.policy_evaluations(policy_id)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_evaluations_decision ON policy.policy_evaluations(decision)"))

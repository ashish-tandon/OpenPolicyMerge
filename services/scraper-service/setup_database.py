#!/usr/bin/env python3
"""
Database setup script for OpenPolicy Scraper Service

This script initializes the database with the necessary tables and schema
for the scraper service to function properly.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Import our configuration
from config import settings

# Database configuration
DATABASE_URL = "postgresql://ashishtandon@localhost:5432/openpolicy"
DB_NAME = "openpolicy"

Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class ScraperInfo(Base):
    """Scraper information table"""
    __tablename__ = 'scraper_info'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    enabled = Column(Boolean, default=True)
    schedule = Column(String(100), default='daily')
    priority = Column(String(50), default='medium')
    jurisdiction_level = Column(String(50), nullable=False)
    source_url = Column(String(500), nullable=False)
    description = Column(Text)
    version = Column(String(50), default='1.0.0')
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    status = Column(String(50), default='idle')
    data_collected = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_duration = Column(Float, default=0.0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScraperJob(Base):
    """Scraper job execution table"""
    __tablename__ = 'scraper_jobs'
    
    id = Column(Integer, primary_key=True)
    scraper_id = Column(Integer, nullable=False)
    status = Column(String(50), default='pending')
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration = Column(Float)
    data_collected = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScraperLog(Base):
    """Scraper execution logs table"""
    __tablename__ = 'scraper_logs'
    
    id = Column(Integer, primary_key=True)
    scraper_id = Column(Integer, nullable=False)
    job_id = Column(Integer)
    level = Column(String(20), default='info')
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    log_data = Column(Text)  # JSON string for additional data

class DataCollection(Base):
    """Data collection tracking table"""
    __tablename__ = 'data_collection'
    
    id = Column(Integer, primary_key=True)
    scraper_id = Column(Integer, nullable=False)
    job_id = Column(Integer)
    data_type = Column(String(100), nullable=False)
    source_url = Column(String(500))
    data_hash = Column(String(64))  # SHA256 hash of collected data
    collected_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="ashishtandon",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully")
        else:
            print(f"Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    
    return True

def create_tables():
    """Create all tables in the database"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(engine)
        print("Tables created successfully")
        
        # Close engine
        engine.dispose()
        
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing"""
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if we already have sample data
        existing_scrapers = session.query(ScraperInfo).count()
        if existing_scrapers > 0:
            print("Sample data already exists, skipping...")
            session.close()
            engine.dispose()
            return True
        
        print("Inserting sample data...")
        
        # Sample scrapers
        sample_scrapers = [
            ScraperInfo(
                name="parliament_ca",
                jurisdiction_level="federal",
                source_url="https://www.parl.ca",
                description="Federal parliamentary data scraper",
                schedule="0 2 * * *"
            ),
            ScraperInfo(
                name="ca_on",
                jurisdiction_level="provincial",
                source_url="https://www.ola.org",
                description="Ontario provincial data scraper",
                schedule="0 3 * * *"
            ),
            ScraperInfo(
                name="ca_on_toronto",
                jurisdiction_level="municipal",
                source_url="https://www.toronto.ca",
                description="Toronto municipal data scraper",
                schedule="0 4 * * *"
            )
        ]
        
        # Add to session
        for scraper in sample_scrapers:
            session.add(scraper)
        
        # Commit changes
        session.commit()
        print(f"Inserted {len(sample_scrapers)} sample scrapers")
        
        # Close session
        session.close()
        engine.dispose()
        
        return True
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False

def verify_database():
    """Verify that the database is working correctly"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
            print("✓ Database connection verified")
        
        # Check tables
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['scraper_info', 'scraper_jobs', 'scraper_logs', 'data_collection']
        for table in expected_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' missing")
        
        # Check sample data
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM scraper_info"))
            count = result.scalar()
            print(f"✓ Found {count} scrapers in database")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"Error verifying database: {e}")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("🚀 OpenPolicy Scraper Service - Database Setup")
    print("=" * 50)
    
    # Step 1: Create database
    print("\n1. Setting up database...")
    if not create_database():
        print("❌ Failed to create database")
        return False
    
    # Step 2: Create tables
    print("\n2. Creating tables...")
    if not create_tables():
        print("❌ Failed to create tables")
        return False
    
    # Step 3: Insert sample data
    print("\n3. Inserting sample data...")
    if not insert_sample_data():
        print("❌ Failed to insert sample data")
        return False
    
    # Step 4: Verify database
    print("\n4. Verifying database...")
    if not verify_database():
        print("❌ Database verification failed")
        return False
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Run tests: python -m pytest tests/")
    print("2. Start the service: python src/main.py")
    print("3. Check database: psql -d openpolicy -c '\\dt'")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

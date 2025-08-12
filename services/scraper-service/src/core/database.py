"""
Database connection and session management for OpenPolicy Scraper Service
"""

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from config import settings

# Database engine
engine = None
async_engine = None
SessionLocal = None

def init_db():
    """Initialize database connection"""
    global engine, async_engine, SessionLocal
    
    try:
        # Create sync engine for compatibility
        engine = create_engine(
            settings.database.url,
            poolclass=QueuePool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            echo=settings.database.echo,
            pool_pre_ping=True
        )
        
        # Create async engine
        async_url = settings.database.url.replace('postgresql://', 'postgresql+asyncpg://')
        async_engine = create_async_engine(
            async_url,
            poolclass=QueuePool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            echo=settings.database.echo,
            pool_pre_ping=True
        )
        
        # Create session factory
        SessionLocal = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False
        )
        
        print("Database connection initialized successfully")
        return True
        
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return False

async def init_db_async():
    """Initialize database connection asynchronously"""
    global async_engine, SessionLocal
    
    try:
        # Create async engine
        async_url = settings.database.url.replace('postgresql://', 'postgresql+asyncpg://')
        async_engine = create_async_engine(
            async_url,
            poolclass=QueuePool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            echo=settings.database.echo,
            pool_pre_ping=True
        )
        
        print("Async database connection initialized successfully")
        return True
        
    except Exception as e:
        print(f"Failed to initialize async database: {e}")
        return False

def get_db():
    """Get database session"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db_async():
    """Get async database session"""
    if async_engine is None:
        raise RuntimeError("Async database not initialized")
    
    async with AsyncSession(async_engine) as session:
        yield session

async def check_db_connection():
    """Check database connection"""
    try:
        if engine:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        return False
    except Exception:
        return False

async def close_db():
    """Close database connections"""
    global engine, async_engine
    
    if engine:
        engine.dispose()
        engine = None
    
    if async_engine:
        await async_engine.dispose()
        async_engine = None
    
    print("Database connections closed")

def execute_query(query: str, params: dict = None):
    """Execute a database query"""
    if engine is None:
        raise RuntimeError("Database not initialized")
    
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchall()

async def execute_query_async(query: str, params: dict = None):
    """Execute a database query asynchronously"""
    if async_engine is None:
        raise RuntimeError("Async database not initialized")
    
    async with async_engine.connect() as conn:
        result = await conn.execute(text(query), params or {})
        return result.fetchall()

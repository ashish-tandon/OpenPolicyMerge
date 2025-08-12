"""
Database connection and session management for the ETL service.
"""
import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from config import get_settings
from models import Base

# Global settings
settings = get_settings()

# Database engine (synchronous for migrations)
engine = None
SessionLocal = None

# Async database engine
async_engine = None
AsyncSessionLocal = None


def create_sync_engine():
    """Create synchronous database engine."""
    global engine, SessionLocal
    
    if engine is None:
        engine = create_engine(
            settings.database.url,
            poolclass=QueuePool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            echo=settings.database.echo,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
        )
        
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    
    return engine


def create_async_engine():
    """Create asynchronous database engine."""
    global async_engine, AsyncSessionLocal
    
    if async_engine is None:
        # Convert PostgreSQL URL to async format
        async_url = settings.database.url.replace('postgresql://', 'postgresql+asyncpg://')
        
        async_engine = create_async_engine(
            async_url,
            echo=settings.database.echo,
            pool_pre_ping=True
        )
        
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    return async_engine


async def init_db():
    """Initialize database connection and create tables."""
    try:
        # Create async engine
        create_async_engine()
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections."""
    global async_engine
    
    if async_engine:
        await async_engine.dispose()
        print("✅ Database connections closed")


def get_db() -> Session:
    """Get synchronous database session."""
    if SessionLocal is None:
        create_sync_engine()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get asynchronous database session."""
    if AsyncSessionLocal is None:
        create_async_engine()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@contextmanager
def get_db_context():
    """Get database session context manager."""
    if SessionLocal is None:
        create_sync_engine()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def check_db_connection() -> bool:
    """Check database connection health."""
    try:
        if async_engine is None:
            create_async_engine()
        
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


async def get_db_stats() -> dict:
    """Get database statistics."""
    try:
        if async_engine is None:
            create_async_engine()
        
        async with async_engine.begin() as conn:
            # Get table counts
            result = await conn.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes
                FROM pg_stat_user_tables
                ORDER BY n_tup_ins DESC
            """)
            
            tables = [dict(row._mapping) for row in result]
            
            # Get connection info
            conn_result = await conn.execute("""
                SELECT 
                    count(*) as active_connections,
                    state
                FROM pg_stat_activity 
                WHERE state IS NOT NULL
                GROUP BY state
            """)
            
            connections = [dict(row._mapping) for row in conn_result]
            
            return {
                "status": "healthy",
                "tables": tables,
                "connections": connections,
                "pool_size": settings.database.pool_size,
                "max_overflow": settings.database.max_overflow
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def run_migrations():
    """Run database migrations."""
    try:
        from alembic import command
        from alembic.config import Config
        
        # Create Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Run migration
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully")
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        raise


def create_tables():
    """Create database tables."""
    try:
        if engine is None:
            create_sync_engine()
        
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        raise


def drop_tables():
    """Drop all database tables (use with caution!)."""
    try:
        if engine is None:
            create_sync_engine()
        
        Base.metadata.drop_all(bind=engine)
        print("✅ Database tables dropped successfully")
        
    except Exception as e:
        print(f"❌ Table dropping failed: {e}")
        raise


# Database health check function
async def health_check() -> dict:
    """Perform database health check."""
    connection_healthy = await check_db_connection()
    
    if connection_healthy:
        try:
            stats = await get_db_stats()
            return {
                "status": "healthy",
                "database": stats,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            return {
                "status": "degraded",
                "database": {
                    "status": "error",
                    "error": str(e)
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
    else:
        return {
            "status": "unhealthy",
            "database": {
                "status": "unhealthy",
                "error": "Cannot connect to database"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }

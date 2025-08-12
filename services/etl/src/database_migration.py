"""
Database Migration System for OpenPolicy Platform
Handles schema creation, updates, and versioning without external dependencies.
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Database migration system for managing schema changes."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine: Optional[Engine] = None
        self.metadata = MetaData()
        self.migration_table = "schema_migrations"
        
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.engine = create_engine(self.database_url)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def create_migration_table(self) -> bool:
        """Create the migration tracking table if it doesn't exist."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {self.migration_table} (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        checksum VARCHAR(64),
                        execution_time_ms INTEGER,
                        status VARCHAR(20) DEFAULT 'success',
                        error_message TEXT
                    )
                """))
                conn.commit()
            logger.info("Migration table created successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to create migration table: {e}")
            return False
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migration versions."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT version FROM {self.migration_table} ORDER BY version"))
                return [row[0] for row in result.fetchall()]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def record_migration(self, version: str, name: str, checksum: str, 
                        execution_time_ms: int, status: str = 'success', 
                        error_message: str = None) -> bool:
        """Record a migration execution."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"""
                    INSERT INTO {self.migration_table} 
                    (version, name, checksum, execution_time_ms, status, error_message)
                    VALUES (:version, :name, :checksum, :execution_time_ms, :status, :error_message)
                """), {
                    'version': version,
                    'name': name,
                    'checksum': checksum,
                    'execution_time_ms': execution_time_ms,
                    'status': status,
                    'error_message': error_message
                })
                conn.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to record migration: {e}")
            return False
    
    def execute_migration(self, version: str, name: str, sql_commands: List[str]) -> bool:
        """Execute a migration with the given SQL commands."""
        start_time = datetime.now()
        
        try:
            with self.engine.connect() as conn:
                for i, sql in enumerate(sql_commands):
                    logger.info(f"Executing migration {version} step {i+1}/{len(sql_commands)}")
                    conn.execute(text(sql))
                
                conn.commit()
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                checksum = self._calculate_checksum(sql_commands)
                
                self.record_migration(version, name, checksum, int(execution_time))
                logger.info(f"Migration {version} ({name}) executed successfully")
                return True
                
        except SQLAlchemyError as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            checksum = self._calculate_checksum(sql_commands)
            
            self.record_migration(version, name, checksum, int(execution_time), 
                                'failed', str(e))
            logger.error(f"Migration {version} ({name}) failed: {e}")
            return False
    
    def _calculate_checksum(self, sql_commands: List[str]) -> str:
        """Calculate checksum for SQL commands."""
        import hashlib
        content = '\n'.join(sql_commands)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def create_service_schemas(self) -> bool:
        """Create schemas for all services."""
        schemas = [
            'policy', 'search', 'auth', 'notification', 'config', 
            'monitoring', 'etl', 'scraper', 'health'
        ]
        
        try:
            with self.engine.connect() as conn:
                for schema in schemas:
                    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                conn.commit()
            logger.info("Service schemas created successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to create service schemas: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """Run all pending migrations."""
        if not self.connect():
            return False
        
        if not self.create_migration_table():
            return False
        
        if not self.create_service_schemas():
            return False
        
        # Get applied migrations
        applied = self.get_applied_migrations()
        
        # Define migrations
        migrations = self._get_migration_definitions()
        
        success_count = 0
        total_count = len(migrations)
        
        for migration in migrations:
            if migration['version'] in applied:
                logger.info(f"Migration {migration['version']} already applied, skipping")
                continue
            
            logger.info(f"Running migration {migration['version']}: {migration['name']}")
            
            if self.execute_migration(
                migration['version'], 
                migration['name'], 
                migration['sql_commands']
            ):
                success_count += 1
            else:
                logger.error(f"Migration {migration['version']} failed, stopping")
                break
        
        logger.info(f"Migrations completed: {success_count}/{total_count} successful")
        return success_count == total_count
    
    def _get_migration_definitions(self) -> List[Dict[str, Any]]:
        """Get all migration definitions."""
        return [
            {
                'version': '001_initial_schemas',
                'name': 'Create initial service schemas',
                'sql_commands': [
                    "CREATE SCHEMA IF NOT EXISTS policy",
                    "CREATE SCHEMA IF NOT EXISTS search", 
                    "CREATE SCHEMA IF NOT EXISTS auth",
                    "CREATE SCHEMA IF NOT EXISTS notification",
                    "CREATE SCHEMA IF NOT EXISTS config",
                    "CREATE SCHEMA IF NOT EXISTS monitoring",
                    "CREATE SCHEMA IF NOT EXISTS etl",
                    "CREATE SCHEMA IF NOT EXISTS scraper",
                    "CREATE SCHEMA IF NOT EXISTS health"
                ]
            },
            {
                'version': '002_policy_service_tables',
                'name': 'Create Policy Service tables',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS policy.policies (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        content TEXT NOT NULL,
                        version VARCHAR(50) NOT NULL,
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by UUID,
                        tags JSONB,
                        metadata JSONB
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS policy.policy_evaluations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        policy_id UUID REFERENCES policy.policies(id),
                        input_data JSONB NOT NULL,
                        result JSONB NOT NULL,
                        evaluation_time_ms INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS policy.policy_rules (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        policy_id UUID REFERENCES policy.policies(id),
                        rule_name VARCHAR(255) NOT NULL,
                        rule_content TEXT NOT NULL,
                        priority INTEGER DEFAULT 0,
                        enabled BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ]
            },
            {
                'version': '003_search_service_tables',
                'name': 'Create Search Service tables',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS search.search_indices (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        document_type VARCHAR(100) NOT NULL,
                        document_id VARCHAR(255) NOT NULL,
                        title TEXT,
                        content TEXT NOT NULL,
                        search_vector TSVECTOR,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_search_indices_search_vector 
                    ON search.search_indices USING GIN(search_vector)
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_search_indices_document_type 
                    ON search.search_indices(document_type)
                    """
                ]
            },
            {
                'version': '004_auth_service_tables',
                'name': 'Create Auth Service tables',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS auth.users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        is_active BOOLEAN DEFAULT true,
                        is_verified BOOLEAN DEFAULT false,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS auth.roles (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(100) UNIQUE NOT NULL,
                        description TEXT,
                        permissions JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS auth.user_roles (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID REFERENCES auth.users(id),
                        role_id UUID REFERENCES auth.roles(id),
                        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, role_id)
                    )
                    """
                ]
            },
            {
                'version': '005_notification_service_tables',
                'name': 'Create Notification Service tables',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS notification.notifications (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        message TEXT NOT NULL,
                        channel VARCHAR(50) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        sent_at TIMESTAMP,
                        read_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS notification.notification_templates (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(100) UNIQUE NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        title_template TEXT NOT NULL,
                        message_template TEXT NOT NULL,
                        variables JSONB,
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ]
            },
            {
                'version': '006_config_service_tables',
                'name': 'Create Config Service tables',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS config.configurations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        key VARCHAR(255) UNIQUE NOT NULL,
                        value JSONB NOT NULL,
                        description TEXT,
                        service VARCHAR(100),
                        environment VARCHAR(50) DEFAULT 'default',
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS config.configuration_audit (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        config_id UUID REFERENCES config.configurations(id),
                        action VARCHAR(50) NOT NULL,
                        old_value JSONB,
                        new_value JSONB,
                        changed_by UUID,
                        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ]
            },
            {
                'version': '007_monitoring_service_tables',
                'name': 'Create Monitoring Service tables',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS monitoring.service_health (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        service_name VARCHAR(100) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        response_time_ms INTEGER,
                        last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        details JSONB
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS monitoring.metrics (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        service_name VARCHAR(100) NOT NULL,
                        metric_name VARCHAR(100) NOT NULL,
                        metric_value NUMERIC NOT NULL,
                        metric_type VARCHAR(50),
                        tags JSONB,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ]
            },
            {
                'version': '008_health_service_tables',
                'name': 'Create Health Service tables',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS health.health_checks (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        service_name VARCHAR(100) NOT NULL,
                        check_type VARCHAR(50) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        response_time_ms INTEGER,
                        error_message TEXT,
                        details JSONB,
                        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_health_checks_service_status 
                    ON health.health_checks(service_name, status)
                    """
                ]
            }
        ]
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration."""
        # This would require implementing rollback logic for each migration
        # For now, we'll log that rollback is not implemented
        logger.warning(f"Rollback for migration {version} is not implemented yet")
        return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        try:
            with self.engine.connect() as conn:
                # Get applied migrations
                applied_result = conn.execute(text(f"SELECT version, name, applied_at, status FROM {self.migration_table} ORDER BY version"))
                applied_migrations = [
                    {
                        'version': row[0],
                        'name': row[1],
                        'applied_at': row[2],
                        'status': row[3]
                    }
                    for row in applied_result.fetchall()
                ]
                
                # Get all defined migrations
                defined_migrations = self._get_migration_definitions()
                
                # Calculate status
                total_migrations = len(defined_migrations)
                applied_count = len([m for m in applied_migrations if m['status'] == 'success'])
                failed_count = len([m for m in applied_migrations if m['status'] == 'failed'])
                pending_count = total_migrations - applied_count - failed_count
                
                return {
                    'total_migrations': total_migrations,
                    'applied_count': applied_count,
                    'failed_count': failed_count,
                    'pending_count': pending_count,
                    'applied_migrations': applied_migrations,
                    'defined_migrations': defined_migrations
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to get migration status: {e}")
            return {}

def main():
    """Main function to run migrations."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python database_migration.py <database_url>")
        sys.exit(1)
    
    database_url = sys.argv[1]
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migrations
    migrator = DatabaseMigration(database_url)
    
    if migrator.run_migrations():
        print("✅ All migrations completed successfully!")
        
        # Show status
        status = migrator.get_migration_status()
        print(f"\n📊 Migration Status:")
        print(f"   Total: {status.get('total_migrations', 0)}")
        print(f"   Applied: {status.get('applied_count', 0)}")
        print(f"   Failed: {status.get('failed_count', 0)}")
        print(f"   Pending: {status.get('pending_count', 0)}")
        
    else:
        print("❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

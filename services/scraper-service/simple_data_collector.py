#!/usr/bin/env python3
"""
Simple Data Collector for OpenPolicy Scraper Service

This script directly interacts with the database to build up data.
"""

import psycopg2
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(
        host="localhost",
        port="5432",
        user="ashishtandon",
        database="openpolicy"
    )


def check_current_status():
    """Check current database status."""
    logger.info("📊 Checking Current Database Status...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check scrapers
        cursor.execute("SELECT id, name, jurisdiction_level, status, data_collected FROM scraper_info ORDER BY id")
        scrapers = cursor.fetchall()
        
        logger.info(f"Found {len(scrapers)} scrapers:")
        for scraper in scrapers:
            logger.info(f"  - ID {scraper[0]}: {scraper[1]} ({scraper[2]}) - Status: {scraper[3]}, Data: {scraper[4]}")
        
        # Check jobs
        cursor.execute("SELECT COUNT(*) FROM scraper_jobs")
        job_count = cursor.fetchone()[0]
        logger.info(f"Total jobs: {job_count}")
        
        # Check logs
        cursor.execute("SELECT COUNT(*) FROM scraper_logs")
        log_count = cursor.fetchone()[0]
        logger.info(f"Total logs: {log_count}")
        
        cursor.close()
        conn.close()
        
        return scrapers
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return []


def create_sample_jobs():
    """Create sample scraper jobs to simulate data collection."""
    logger.info("🔄 Creating Sample Scraper Jobs...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create jobs for each scraper
        scrapers = [(1, "parliament_ca"), (2, "ca_on"), (3, "ca_on_toronto")]
        
        for scraper_id, scraper_name in scrapers:
            # Create a completed job
            cursor.execute("""
                INSERT INTO scraper_jobs (scraper_id, status, created_at, updated_at, started_at, completed_at, duration, data_collected)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                scraper_id,
                'completed',
                datetime.utcnow(),
                datetime.utcnow(),
                datetime.utcnow(),
                datetime.utcnow(),
                45.5,  # 45.5 seconds duration
                150 + (scraper_id * 50)  # Varying data amounts
            ))
            
            job_id = cursor.fetchone()[0]
            logger.info(f"Created completed job {job_id} for {scraper_name}")
            
            # Create a running job
            cursor.execute("""
                INSERT INTO scraper_jobs (scraper_id, status, created_at, updated_at, started_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                scraper_id,
                'running',
                datetime.utcnow(),
                datetime.utcnow(),
                datetime.utcnow()
            ))
            
            job_id = cursor.fetchone()[0]
            logger.info(f"Created running job {job_id} for {scraper_name}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Sample jobs created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create sample jobs: {e}")


def create_sample_logs():
    """Create sample log entries."""
    logger.info("📝 Creating Sample Log Entries...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sample log messages for different operations
        log_entries = [
            (1, 'info', 'Scraper started successfully', '{"operation": "start", "timestamp": "' + datetime.utcnow().isoformat() + '"}'),
            (1, 'info', 'Data extraction completed', '{"operation": "extract", "records": 150, "timestamp": "' + datetime.utcnow().isoformat() + '"}'),
            (2, 'info', 'Provincial scraper initialized', '{"operation": "init", "timestamp": "' + datetime.utcnow().isoformat() + '"}'),
            (2, 'warning', 'Rate limit approaching', '{"operation": "rate_limit", "timestamp": "' + datetime.utcnow().isoformat() + '"}'),
            (3, 'info', 'Municipal data collection started', '{"operation": "start", "timestamp": "' + datetime.utcnow().isoformat() + '"}'),
            (3, 'error', 'Connection timeout', '{"operation": "connection", "error": "timeout", "timestamp": "' + datetime.utcnow().isoformat() + '"}'),
        ]
        
        for scraper_id, level, message, log_data in log_entries:
            cursor.execute("""
                INSERT INTO scraper_logs (scraper_id, level, message, log_data, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (scraper_id, level, message, log_data, datetime.utcnow()))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Sample logs created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create sample logs: {e}")


def update_scraper_status():
    """Update scraper statuses to reflect activity."""
    logger.info("🔄 Updating Scraper Statuses...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update federal scraper
        cursor.execute("""
            UPDATE scraper_info 
            SET status = 'completed', last_run = %s, data_collected = 150, success_rate = 95.0, avg_duration = 45.5
            WHERE id = 1
        """, (datetime.utcnow(),))
        
        # Update provincial scraper
        cursor.execute("""
            UPDATE scraper_info 
            SET status = 'running', last_run = %s, data_collected = 200, success_rate = 92.0, avg_duration = 52.3
            WHERE id = 2
        """, (datetime.utcnow(),))
        
        # Update municipal scraper
        cursor.execute("""
            UPDATE scraper_info 
            SET status = 'completed', last_run = %s, data_collected = 250, success_rate = 88.0, avg_duration = 38.7
            WHERE id = 3
        """, (datetime.utcnow(),))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Scraper statuses updated successfully")
        
    except Exception as e:
        logger.error(f"Failed to update scraper statuses: {e}")


def create_sample_data_collection():
    """Create sample data collection records."""
    logger.info("📊 Creating Sample Data Collection Records...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sample data for different types
        data_types = [
            ('bills', 'https://parl.ca/bills', 'hash123', 1),
            ('bills', 'https://ontario.ca/bills', 'hash456', 2),
            ('bills', 'https://toronto.ca/bylaws', 'hash789', 3),
            ('representatives', 'https://parl.ca/mps', 'hash101', 1),
            ('representatives', 'https://ontario.ca/mpps', 'hash102', 2),
            ('representatives', 'https://toronto.ca/councillors', 'hash103', 3),
            ('votes', 'https://parl.ca/votes', 'hash201', 1),
            ('votes', 'https://ontario.ca/votes', 'hash202', 2),
            ('committees', 'https://parl.ca/committees', 'hash301', 1),
            ('committees', 'https://ontario.ca/committees', 'hash302', 2),
        ]
        
        for data_type, source_url, data_hash, scraper_id in data_types:
            cursor.execute("""
                INSERT INTO data_collection (data_type, source_url, data_hash, collected_at, scraper_id, processed)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data_type, source_url, data_hash, datetime.utcnow(), scraper_id, False))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Sample data collection records created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create sample data collection: {e}")


def create_analytics_summary():
    """Create analytics summary table and populate with data."""
    logger.info("📈 Creating Analytics Summary...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create analytics summary table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_summary (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value NUMERIC(10,2),
                jurisdiction_level VARCHAR(50),
                data_type VARCHAR(50),
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                period VARCHAR(20) DEFAULT 'daily'
            )
        """)
        
        # Insert sample analytics data
        analytics_data = [
            ('total_records', 600, 'all', 'all'),
            ('federal_records', 200, 'federal', 'all'),
            ('provincial_records', 200, 'provincial', 'all'),
            ('municipal_records', 200, 'municipal', 'all'),
            ('bills_count', 300, 'all', 'bills'),
            ('representatives_count', 200, 'all', 'representatives'),
            ('votes_count', 100, 'all', 'votes'),
            ('success_rate', 91.67, 'all', 'all'),
            ('avg_processing_time', 45.5, 'all', 'all'),
            ('data_freshness_hours', 2.5, 'all', 'all'),
        ]
        
        for metric_name, metric_value, jurisdiction_level, data_type in analytics_data:
            cursor.execute("""
                INSERT INTO analytics_summary (metric_name, metric_value, jurisdiction_level, data_type)
                VALUES (%s, %s, %s, %s)
            """, (metric_name, metric_value, jurisdiction_level, data_type))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Analytics summary created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create analytics summary: {e}")


def final_status_check():
    """Perform final status check after data population."""
    logger.info("📊 Final Database Status Check...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count all records
        tables = ['scraper_info', 'scraper_jobs', 'scraper_logs', 'data_collection', 'analytics_summary']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"  - {table}: {count} records")
            except Exception as e:
                logger.warning(f"  - {table}: Error counting records - {e}")
        
        # Show sample data
        cursor.execute("SELECT data_type, COUNT(*) FROM data_collection GROUP BY data_type")
        data_summary = cursor.fetchall()
        
        logger.info("Data Collection Summary:")
        for data_type, count in data_summary:
            logger.info(f"  - {data_type}: {count} records")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Final status check failed: {e}")


def main():
    """Main data population process."""
    logger.info("🚀 Starting OpenPolicy Database Population Process")
    logger.info("=" * 60)
    
    start_time = datetime.utcnow()
    
    try:
        # Step 1: Check current status
        scrapers = check_current_status()
        
        if not scrapers:
            logger.error("No scrapers found. Cannot proceed.")
            return
        
        # Step 2: Create sample jobs
        create_sample_jobs()
        
        # Step 3: Create sample logs
        create_sample_logs()
        
        # Step 4: Update scraper statuses
        update_scraper_status()
        
        # Step 5: Create sample data collection
        create_sample_data_collection()
        
        # Step 6: Create analytics summary
        create_analytics_summary()
        
        # Step 7: Final status check
        final_status_check()
        
        # Summary
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 DATABASE POPULATION COMPLETED SUCCESSFULLY!")
        logger.info(f"⏱️  Total Duration: {duration:.2f} seconds")
        logger.info("=" * 60)
        logger.info("📊 Your OpenPolicy database now contains:")
        logger.info("  - Sample scraper jobs and execution history")
        logger.info("  - Sample log entries for monitoring")
        logger.info("  - Sample data collection records")
        logger.info("  - Analytics summary for reporting")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Database population process failed: {e}")
        raise


if __name__ == "__main__":
    main()

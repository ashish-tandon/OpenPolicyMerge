#!/usr/bin/env python3
"""
Data Collection Script for OpenPolicy Scraper Service

This script runs the scrapers to collect real data and build up the database.
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
import json

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.scraper_manager import ScraperManager
from src.services.data_pipeline import DataPipeline
from src.services.etl_service import ETLService
from src.core.database import get_db_async

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def collect_federal_data():
    """Collect federal parliamentary data."""
    logger.info("🌍 Starting Federal Data Collection...")
    
    try:
        async with ScraperManager() as scraper_manager:
            # Get federal scraper
            scrapers = await scraper_manager.get_scrapers(
                enabled_only=True, 
                jurisdiction_level="federal"
            )
            
            if not scrapers:
                logger.error("No federal scrapers found")
                return
                
            scraper = scrapers[0]
            logger.info(f"Running federal scraper: {scraper.name}")
            
            # Run the scraper
            job = await scraper_manager.run_scraper(scraper.id)
            logger.info(f"Federal scraper job created: {job.id}")
            
            # Wait for completion
            await asyncio.sleep(2)
            
            # Get job status
            updated_job = await scraper_manager.get_jobs(scraper_id=scraper.id, limit=1)
            if updated_job:
                job = updated_job[0]
                logger.info(f"Federal job status: {job.status}")
                logger.info(f"Federal data collected: {getattr(job, 'data_collected', 0)}")
            
    except Exception as e:
        logger.error(f"Federal data collection failed: {e}")


async def collect_provincial_data():
    """Collect provincial data."""
    logger.info("🏛️ Starting Provincial Data Collection...")
    
    try:
        async with ScraperManager() as scraper_manager:
            # Get provincial scrapers
            scrapers = await scraper_manager.get_scrapers(
                enabled_only=True, 
                jurisdiction_level="provincial"
            )
            
            if not scrapers:
                logger.error("No provincial scrapers found")
                return
                
            scraper = scrapers[0]
            logger.info(f"Running provincial scraper: {scraper.name}")
            
            # Run the scraper
            job = await scraper_manager.run_scraper(scraper.id)
            logger.info(f"Provincial scraper job created: {job.id}")
            
            # Wait for completion
            await asyncio.sleep(2)
            
            # Get job status
            updated_job = await scraper_manager.get_jobs(scraper_id=scraper.id, limit=1)
            if updated_job:
                job = updated_job[0]
                logger.info(f"Provincial job status: {job.status}")
                logger.info(f"Provincial data collected: {getattr(job, 'data_collected', 0)}")
            
    except Exception as e:
        logger.error(f"Provincial data collection failed: {e}")


async def collect_municipal_data():
    """Collect municipal data."""
    logger.info("🏙️ Starting Municipal Data Collection...")
    
    try:
        async with ScraperManager() as scraper_manager:
            # Get municipal scrapers
            scrapers = await scraper_manager.get_scrapers(
                enabled_only=True, 
                jurisdiction_level="municipal"
            )
            
            if not scrapers:
                logger.error("No municipal scrapers found")
                return
                
            scraper = scrapers[0]
            logger.info(f"Running municipal scraper: {scraper.name}")
            
            # Run the scraper
            job = await scraper_manager.run_scraper(scraper.id)
            logger.info(f"Municipal scraper job created: {job.id}")
            
            # Wait for completion
            await asyncio.sleep(2)
            
            # Get job status
            updated_job = await scraper_manager.get_jobs(scraper_id=scraper.id, limit=1)
            if updated_job:
                job = updated_job[0]
                logger.info(f"Municipal job status: {job.status}")
                logger.info(f"Municipal data collected: {getattr(job, 'data_collected', 0)}")
            
    except Exception as e:
        logger.error(f"Municipal data collection failed: {e}")


async def run_data_pipeline():
    """Run the data pipeline to process collected data."""
    logger.info("🔄 Starting Data Pipeline Processing...")
    
    try:
        async with DataPipeline() as pipeline:
            # Process bills data
            logger.info("Processing bills data...")
            bills_data = await pipeline.extract_data(1, "bills")
            logger.info(f"Extracted {len(bills_data)} bills")
            
            # Transform bills data
            transformed_bills = await pipeline.transform_data(bills_data)
            logger.info(f"Transformed {len(transformed_bills)} bills")
            
            # Load bills data
            load_result = await pipeline.load_data(
                transformed_bills, 
                {"type": "database", "table": "bills"}
            )
            logger.info(f"Loaded bills: {load_result}")
            
            # Process representatives data
            logger.info("Processing representatives data...")
            reps_data = await pipeline.extract_data(1, "representatives")
            logger.info(f"Extracted {len(reps_data)} representatives")
            
            # Transform representatives data
            transformed_reps = await pipeline.transform_data(reps_data)
            logger.info(f"Transformed {len(transformed_reps)} representatives")
            
            # Load representatives data
            load_result = await pipeline.load_data(
                transformed_reps, 
                {"type": "database", "table": "representatives"}
            )
            logger.info(f"Loaded representatives: {load_result}")
            
    except Exception as e:
        logger.error(f"Data pipeline processing failed: {e}")


async def run_etl_workflow():
    """Run ETL workflow for data processing."""
    logger.info("⚙️ Starting ETL Workflow...")
    
    try:
        async with ETLService() as etl_service:
            # Create a workflow
            workflow_config = {
                "name": "Daily Data Processing",
                "steps": [
                    {
                        "type": "extract",
                        "name": "Extract All Data",
                        "source": {
                            "type": "database",
                            "query": "SELECT * FROM scraper_jobs WHERE status = 'completed'"
                        }
                    },
                    {
                        "type": "transform",
                        "name": "Transform Data",
                        "rules": [
                            "clean_whitespace",
                            "validate_required_fields",
                            "convert_data_types"
                        ]
                    },
                    {
                        "type": "load",
                        "name": "Load to Analytics",
                        "destination": {
                            "type": "database",
                            "table": "analytics_summary"
                        }
                    }
                ],
                "schedule": "daily"
            }
            
            workflow_id = await etl_service.create_workflow(workflow_config)
            logger.info(f"Created ETL workflow: {workflow_id}")
            
            # Execute the workflow
            result = await etl_service.execute_workflow(workflow_id)
            logger.info(f"ETL workflow executed: {result['success']}")
            
    except Exception as e:
        logger.error(f"ETL workflow failed: {e}")


async def check_database_status():
    """Check the current status of the database."""
    logger.info("📊 Checking Database Status...")
    
    try:
        # Check scraper status
        async with ScraperManager() as scraper_manager:
            scrapers = await scraper_manager.get_scrapers()
            logger.info(f"Total scrapers: {len(scrapers)}")
            
            for scraper in scrapers:
                logger.info(f"  - {scraper.name}: {scraper.status}, Data: {scraper.data_collected}")
            
            # Check jobs
            jobs = await scraper_manager.get_jobs(limit=10)
            logger.info(f"Recent jobs: {len(jobs)}")
            
            for job in jobs:
                logger.info(f"  - Job {job.id}: {job.status}, Scraper: {job.scraper_id}")
        
        # Check database tables
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="ashishtandon",
            database="openpolicy"
        )
        cursor = conn.cursor()
        
        # Count records in key tables
        cursor.execute("SELECT COUNT(*) FROM scraper_info")
        scraper_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scraper_jobs")
        job_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scraper_logs")
        log_count = cursor.fetchone()[0]
        
        logger.info(f"Database Records:")
        logger.info(f"  - Scrapers: {scraper_count}")
        logger.info(f"  - Jobs: {job_count}")
        logger.info(f"  - Logs: {log_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Database status check failed: {e}")


async def main():
    """Main data collection process."""
    logger.info("🚀 Starting OpenPolicy Data Collection Process")
    logger.info("=" * 60)
    
    start_time = datetime.utcnow()
    
    try:
        # Step 1: Check current status
        await check_database_status()
        
        # Step 2: Collect data from all jurisdictions
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: COLLECTING DATA FROM ALL JURISDICTIONS")
        logger.info("=" * 60)
        
        await collect_federal_data()
        await collect_provincial_data()
        await collect_municipal_data()
        
        # Step 3: Process data through pipeline
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: PROCESSING DATA THROUGH PIPELINE")
        logger.info("=" * 60)
        
        await run_data_pipeline()
        
        # Step 4: Run ETL workflow
        logger.info("\n" + "=" * 60)
        logger.info("STEP 4: RUNNING ETL WORKFLOW")
        logger.info("=" * 60)
        
        await run_etl_workflow()
        
        # Step 5: Final status check
        logger.info("\n" + "=" * 60)
        logger.info("STEP 5: FINAL STATUS CHECK")
        logger.info("=" * 60)
        
        await check_database_status()
        
        # Summary
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 DATA COLLECTION PROCESS COMPLETED SUCCESSFULLY!")
        logger.info(f"⏱️  Total Duration: {duration:.2f} seconds")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Data collection process failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

"""
Data Extraction Tasks for ETL Service

Handles extraction of data from various sources including parliamentary data,
civic data, and external APIs.
"""

from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests
import pandas as pd
import logging
from typing import Dict, List, Any, Optional

from database import get_db
from models.etl_job import ETLJob
from models.data_source import DataSource
from models.processing_log import ProcessingLog
from core.logging import get_logger

logger = get_logger(__name__)

@shared_task(bind=True, name="extract_parliamentary_data")
def extract_parliamentary_data(self, source_id: Optional[int] = None):
    """
    Extract parliamentary data from various sources
    
    Args:
        source_id: Specific data source ID to extract from
        
    Returns:
        Dict containing extraction results
    """
    task_id = self.request.id
    logger.info(f"Starting parliamentary data extraction task: {task_id}")
    
    try:
        # Create ETL job record
        db = next(get_db())
        job = ETLJob(
            name="parliamentary_data_extraction",
            description=f"Extract parliamentary data from sources",
            job_type="extraction",
            status="running",
            progress=0,
            current_step="initializing",
            total_steps=5
        )
        db.add(job)
        db.commit()
        
        # Get data sources
        if source_id:
            sources = db.query(DataSource).filter(
                DataSource.id == source_id,
                DataSource.source_type == "parliamentary"
            ).all()
        else:
            sources = db.query(DataSource).filter(
                DataSource.source_type == "parliamentary",
                DataSource.is_active == True
            ).all()
        
        if not sources:
            job.status = "failed"
            job.current_step = "no_sources_found"
            db.commit()
            return {"status": "failed", "error": "No parliamentary data sources found"}
        
        total_sources = len(sources)
        extracted_data = []
        
        for i, source in enumerate(sources):
            try:
                logger.info(f"Extracting from source: {source.name}")
                
                # Update job progress
                job.progress = int((i / total_sources) * 100)
                job.current_step = f"extracting_from_{source.name}"
                db.commit()
                
                # Extract data based on source type
                if source.source_type == "api":
                    data = _extract_from_api(source)
                elif source.source_type == "database":
                    data = _extract_from_database(source)
                elif source.source_type == "file":
                    data = _extract_from_file(source)
                else:
                    logger.warning(f"Unknown source type: {source.source_type}")
                    continue
                
                if data:
                    extracted_data.append({
                        "source_id": source.id,
                        "source_name": source.name,
                        "data": data,
                        "extracted_at": datetime.utcnow()
                    })
                    
                    # Update source metrics
                    source.last_extraction = datetime.utcnow()
                    source.extraction_count += 1
                
                # Log successful extraction
                log = ProcessingLog(
                    etl_job_id=job.id,
                    data_source_id=source.id,
                    step="extraction",
                    status="success",
                    message=f"Successfully extracted {len(data) if data else 0} records from {source.name}",
                    metadata={"records_extracted": len(data) if data else 0}
                )
                db.add(log)
                
            except Exception as e:
                logger.error(f"Failed to extract from source {source.name}: {e}")
                
                # Log failure
                log = ProcessingLog(
                    etl_job_id=job.id,
                    data_source_id=source.id,
                    step="extraction",
                    status="failed",
                    message=f"Extraction failed: {str(e)}",
                    metadata={"error": str(e)}
                )
                db.add(log)
                
                # Update source health
                source.health_status = "unhealthy"
                source.last_error = str(e)
                source.error_count += 1
        
        # Finalize job
        job.progress = 100
        job.status = "completed"
        job.current_step = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Parliamentary data extraction completed: {len(extracted_data)} sources processed")
        
        return {
            "status": "success",
            "job_id": job.id,
            "sources_processed": total_sources,
            "sources_successful": len(extracted_data),
            "total_records": sum(len(item["data"]) for item in extracted_data if item["data"]),
            "extracted_data": extracted_data
        }
        
    except Exception as e:
        logger.error(f"Parliamentary data extraction failed: {e}")
        
        if 'job' in locals():
            job.status = "failed"
            job.current_step = "failed"
            job.error_message = str(e)
            db.commit()
        
        return {"status": "failed", "error": str(e)}

@shared_task(bind=True, name="extract_civic_data")
def extract_civic_data(self, source_id: Optional[int] = None):
    """
    Extract civic data from various sources
    
    Args:
        source_id: Specific data source ID to extract from
        
    Returns:
        Dict containing extraction results
    """
    task_id = self.request.id
    logger.info(f"Starting civic data extraction task: {task_id}")
    
    try:
        # Create ETL job record
        db = next(get_db())
        job = ETLJob(
            name="civic_data_extraction",
            description=f"Extract civic data from sources",
            job_type="extraction",
            status="running",
            progress=0,
            current_step="initializing",
            total_steps=5
        )
        db.add(job)
        db.commit()
        
        # Get data sources
        if source_id:
            sources = db.query(DataSource).filter(
                DataSource.id == source_id,
                DataSource.source_type == "civic"
            ).all()
        else:
            sources = db.query(DataSource).filter(
                DataSource.source_type == "civic",
                DataSource.is_active == True
            ).all()
        
        if not sources:
            job.status = "failed"
            job.current_step = "no_sources_found"
            db.commit()
            return {"status": "failed", "error": "No civic data sources found"}
        
        total_sources = len(sources)
        extracted_data = []
        
        for i, source in enumerate(sources):
            try:
                logger.info(f"Extracting from source: {source.name}")
                
                # Update job progress
                job.progress = int((i / total_sources) * 100)
                job.current_step = f"extracting_from_{source.name}"
                db.commit()
                
                # Extract data based on source type
                if source.source_type == "api":
                    data = _extract_from_api(source)
                elif source.source_type == "database":
                    data = _extract_from_database(source)
                elif source.source_type == "file":
                    data = _extract_from_file(source)
                else:
                    logger.warning(f"Unknown source type: {source.source_type}")
                    continue
                
                if data:
                    extracted_data.append({
                        "source_id": source.id,
                        "source_name": source.name,
                        "data": data,
                        "extracted_at": datetime.utcnow()
                    })
                    
                    # Update source metrics
                    source.last_extraction = datetime.utcnow()
                    source.extraction_count += 1
                
                # Log successful extraction
                log = ProcessingLog(
                    etl_job_id=job.id,
                    data_source_id=source.id,
                    step="extraction",
                    status="success",
                    message=f"Successfully extracted {len(data) if data else 0} records from {source.name}",
                    metadata={"records_extracted": len(data) if data else 0}
                )
                db.add(log)
                
            except Exception as e:
                logger.error(f"Failed to extract from source {source.name}: {e}")
                
                # Log failure
                log = ProcessingLog(
                    etl_job_id=job.id,
                    data_source_id=source.id,
                    step="extraction",
                    status="failed",
                    message=f"Extraction failed: {str(e)}",
                    metadata={"error": str(e)}
                )
                db.add(log)
                
                # Update source health
                source.health_status = "unhealthy"
                source.last_error = str(e)
                source.error_count += 1
        
        # Finalize job
        job.progress = 100
        job.status = "completed"
        job.current_step = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Civic data extraction completed: {len(extracted_data)} sources processed")
        
        return {
            "status": "success",
            "job_id": job.id,
            "sources_processed": total_sources,
            "sources_successful": len(extracted_data),
            "total_records": sum(len(item["data"]) for item in extracted_data if item["data"]),
            "extracted_data": extracted_data
        }
        
    except Exception as e:
        logger.error(f"Civic data extraction failed: {e}")
        
        if 'job' in locals():
            job.status = "failed"
            job.current_step = "failed"
            job.error_message = str(e)
            db.commit()
        
        return {"status": "failed", "error": str(e)}

@shared_task(bind=True, name="extract_data_source")
def extract_data_source(self, source_id: int):
    """
    Extract data from a specific source
    
    Args:
        source_id: ID of the data source to extract from
        
    Returns:
        Dict containing extraction results
    """
    task_id = self.request.id
    logger.info(f"Starting data extraction from source {source_id}: {task_id}")
    
    try:
        db = next(get_db())
        source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not source:
            return {"status": "failed", "error": f"Data source {source_id} not found"}
        
        if not source.is_active:
            return {"status": "failed", "error": f"Data source {source.name} is not active"}
        
        # Create ETL job record
        job = ETLJob(
            name=f"extract_from_{source.name}",
            description=f"Extract data from {source.name}",
            job_type="extraction",
            status="running",
            progress=0,
            current_step="initializing",
            total_steps=3
        )
        db.add(job)
        db.commit()
        
        # Extract data
        job.progress = 33
        job.current_step = "extracting"
        db.commit()
        
        if source.source_type == "api":
            data = _extract_from_api(source)
        elif source.source_type == "database":
            data = _extract_from_database(source)
        elif source.source_type == "file":
            data = _extract_from_file(source)
        else:
            raise ValueError(f"Unsupported source type: {source.source_type}")
        
        # Update source metrics
        source.last_extraction = datetime.utcnow()
        source.extraction_count += 1
        source.health_status = "healthy"
        
        # Finalize job
        job.progress = 100
        job.status = "completed"
        job.current_step = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()
        
        # Log success
        log = ProcessingLog(
            etl_job_id=job.id,
            data_source_id=source.id,
            step="extraction",
            status="success",
            message=f"Successfully extracted {len(data) if data else 0} records",
            metadata={"records_extracted": len(data) if data else 0}
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Data extraction from {source.name} completed successfully")
        
        return {
            "status": "success",
            "job_id": job.id,
            "source_name": source.name,
            "records_extracted": len(data) if data else 0,
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Data extraction from source {source_id} failed: {e}")
        
        if 'job' in locals():
            job.status = "failed"
            job.current_step = "failed"
            job.error_message = str(e)
            db.commit()
        
        return {"status": "failed", "error": str(e)}

def _extract_from_api(source: DataSource) -> List[Dict[str, Any]]:
    """Extract data from API source"""
    try:
        response = requests.get(
            source.connection_url,
            headers=source.auth_headers or {},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            if 'data' in data:
                return data['data']
            elif 'results' in data:
                return data['results']
            elif 'items' in data:
                return data['items']
            else:
                return [data]
        elif isinstance(data, list):
            return data
        else:
            return [data]
            
    except Exception as e:
        logger.error(f"API extraction failed for {source.name}: {e}")
        raise

def _extract_from_database(source: DataSource) -> List[Dict[str, Any]]:
    """Extract data from database source"""
    try:
        # This would connect to the source database and execute queries
        # For now, return mock data
        logger.info(f"Database extraction not yet implemented for {source.name}")
        return []
        
    except Exception as e:
        logger.error(f"Database extraction failed for {source.name}: {e}")
        raise

def _extract_from_file(source: DataSource) -> List[Dict[str, Any]]:
    """Extract data from file source"""
    try:
        # This would read from files (CSV, JSON, Excel, etc.)
        # For now, return mock data
        logger.info(f"File extraction not yet implemented for {source.name}")
        return []
        
    except Exception as e:
        logger.error(f"File extraction failed for {source.name}: {e}")
        raise

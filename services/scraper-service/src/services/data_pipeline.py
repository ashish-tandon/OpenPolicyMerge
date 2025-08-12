"""
Data Pipeline Service for OpenPolicy Scraper Service

This module provides ETL (Extract, Transform, Load) functionality for
processing scraped data through a pipeline.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from uuid import uuid4
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..core.database import get_db, get_db_async
from ..core.models import (
    ScraperInfo, ScraperJob, ScraperStatus, JobStatus, DataType
)

logger = logging.getLogger(__name__)


class DataPipeline:
    """Manages data processing pipeline operations."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the data pipeline."""
        self.db_session = db_session
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self.pipeline_lock = asyncio.Lock()
        
    async def __aenter__(self):
        """Async context manager entry."""
        if not self.db_session:
            self.db_session = await anext(get_db_async())
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.db_session and not self.db_session.is_None:
            await self.db_session.close()
    
    # ============================================================================
    # PIPELINE INITIALIZATION
    # ============================================================================
    
    async def initialize_pipeline(self, config: Dict[str, Any]) -> bool:
        """Initialize the data pipeline with configuration."""
        try:
            logger.info("Initializing data pipeline...")
            
            # Validate configuration
            validation_result = await self._validate_pipeline_config(config)
            if not validation_result['valid']:
                logger.error(f"Pipeline configuration validation failed: {validation_result['errors']}")
                return False
            
            # Set up pipeline components
            await self._setup_pipeline_components(config)
            
            logger.info("Data pipeline initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            return False
    
    async def _validate_pipeline_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pipeline configuration."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['extractors', 'transformers', 'loaders']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate extractors
        if 'extractors' in config:
            for extractor in config['extractors']:
                if 'type' not in extractor:
                    errors.append("Extractor missing 'type' field")
                if 'config' not in extractor:
                    warnings.append("Extractor missing 'config' field")
        
        # Validate transformers
        if 'transformers' in config:
            for transformer in config['transformers']:
                if 'type' not in transformer:
                    errors.append("Transformer missing 'type' field")
        
        # Validate loaders
        if 'loaders' in config:
            for loader in config['loaders']:
                if 'type' not in loader:
                    errors.append("Loader missing 'type' field")
                if 'destination' not in loader:
                    errors.append("Loader missing 'destination' field")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def _setup_pipeline_components(self, config: Dict[str, Any]):
        """Set up pipeline components based on configuration."""
        # This would set up actual pipeline components in a real implementation
        logger.info("Setting up pipeline components...")
        
        # Simulate component setup
        await asyncio.sleep(0.1)
        
        logger.info("Pipeline components setup completed")
    
    # ============================================================================
    # DATA EXTRACTION
    # ============================================================================
    
    async def extract_data(self, 
                          scraper_id: int,
                          data_type: str,
                          extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract data from a scraper."""
        try:
            logger.info(f"Extracting data from scraper {scraper_id}, type: {data_type}")
            
            # Get scraper info
            scraper = await self._get_scraper_info(scraper_id)
            if not scraper:
                raise ValueError(f"Scraper {scraper_id} not found")
            
            # Perform extraction based on data type
            if data_type == DataType.BILLS:
                extracted_data = await self._extract_bills(scraper, extraction_config)
            elif data_type == DataType.REPRESENTATIVES:
                extracted_data = await self._extract_representatives(scraper, extraction_config)
            elif data_type == DataType.VOTES:
                extracted_data = await self._extract_votes(scraper, extraction_config)
            else:
                extracted_data = await self._extract_generic_data(scraper, data_type, extraction_config)
            
            # Log extraction
            logger.info(f"Extracted {len(extracted_data)} {data_type} records from scraper {scraper_id}")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Data extraction failed for scraper {scraper_id}: {e}")
            raise
    
    async def _extract_bills(self, scraper: ScraperInfo, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract bills data."""
        # Simulate bill extraction
        await asyncio.sleep(0.5)
        
        return [
            {
                'id': f'bill_{i}',
                'title': f'Sample Bill {i}',
                'description': f'Description for bill {i}',
                'status': 'active',
                'introduced_date': datetime.utcnow().isoformat(),
                'jurisdiction': scraper.jurisdiction_level,
                'source': scraper.name
            }
            for i in range(1, 11)  # Simulate 10 bills
        ]
    
    async def _extract_representatives(self, scraper: ScraperInfo, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract representatives data."""
        # Simulate representative extraction
        await asyncio.sleep(0.3)
        
        return [
            {
                'id': f'rep_{i}',
                'name': f'Representative {i}',
                'party': f'Party {i % 3 + 1}',
                'district': f'District {i}',
                'jurisdiction': scraper.jurisdiction_level,
                'source': scraper.name
            }
            for i in range(1, 16)  # Simulate 15 representatives
        ]
    
    async def _extract_votes(self, scraper: ScraperInfo, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract votes data."""
        # Simulate vote extraction
        await asyncio.sleep(0.2)
        
        return [
            {
                'id': f'vote_{i}',
                'bill_id': f'bill_{i % 5 + 1}',
                'representative_id': f'rep_{i % 10 + 1}',
                'vote': 'yes' if i % 2 == 0 else 'no',
                'date': datetime.utcnow().isoformat(),
                'jurisdiction': scraper.jurisdiction_level,
                'source': scraper.name
            }
            for i in range(1, 21)  # Simulate 20 votes
        ]
    
    async def _extract_generic_data(self, scraper: ScraperInfo, data_type: str, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract generic data of any type."""
        # Simulate generic data extraction
        await asyncio.sleep(0.4)
        
        return [
            {
                'id': f'{data_type}_{i}',
                'type': data_type,
                'content': f'Sample {data_type} data {i}',
                'jurisdiction': scraper.jurisdiction_level,
                'source': scraper.name,
                'extracted_at': datetime.utcnow().isoformat()
            }
            for i in range(1, 6)  # Simulate 5 generic records
        ]
    
    # ============================================================================
    # DATA TRANSFORMATION
    # ============================================================================
    
    async def transform_data(self, 
                           raw_data: List[Dict[str, Any]],
                           transformation_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Transform extracted data."""
        try:
            logger.info(f"Transforming {len(raw_data)} data records")
            
            if not transformation_config:
                transformation_config = self._get_default_transformation_config()
            
            # Apply transformations
            transformed_data = []
            for record in raw_data:
                transformed_record = await self._apply_transformations(record, transformation_config)
                transformed_data.append(transformed_record)
            
            # Validate transformed data
            validation_result = await self._validate_transformed_data(transformed_data)
            if not validation_result['valid']:
                logger.warning(f"Data validation warnings: {validation_result['warnings']}")
            
            logger.info(f"Transformed {len(transformed_data)} data records")
            return transformed_data
            
        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            raise
    
    async def _apply_transformations(self, record: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transformations to a single record."""
        transformed_record = record.copy()
        
        # Apply field mappings
        if 'field_mappings' in config:
            for old_name, new_name in config['field_mappings'].items():
                if old_name in transformed_record:
                    transformed_record[new_name] = transformed_record.pop(old_name)
        
        # Apply data type conversions
        if 'type_conversions' in config:
            for field, target_type in config['type_conversions'].items():
                if field in transformed_record:
                    transformed_record[field] = self._convert_data_type(
                        transformed_record[field], target_type
                    )
        
        # Apply data cleaning
        if config.get('clean_data', True):
            transformed_record = await self._clean_record_data(transformed_record)
        
        # Add metadata
        transformed_record['transformed_at'] = datetime.utcnow().isoformat()
        transformed_record['pipeline_version'] = '1.0.0'
        
        return transformed_record
    
    def _convert_data_type(self, value: Any, target_type: str) -> Any:
        """Convert data to target type."""
        try:
            if target_type == 'string':
                return str(value)
            elif target_type == 'integer':
                return int(value)
            elif target_type == 'float':
                return float(value)
            elif target_type == 'boolean':
                return bool(value)
            elif target_type == 'datetime':
                if isinstance(value, str):
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                return value
            else:
                return value
        except (ValueError, TypeError):
            return value
    
    async def _clean_record_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize record data."""
        cleaned_record = {}
        
        for key, value in record.items():
            if value is not None:
                # Clean string values
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    if cleaned_value:  # Only keep non-empty strings
                        cleaned_record[key] = cleaned_value
                else:
                    cleaned_record[key] = value
        
        return cleaned_record
    
    def _get_default_transformation_config(self) -> Dict[str, Any]:
        """Get default transformation configuration."""
        return {
            'clean_data': True,
            'field_mappings': {},
            'type_conversions': {},
            'validation_rules': []
        }
    
    async def _validate_transformed_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate transformed data."""
        warnings = []
        
        for i, record in enumerate(data):
            # Check for required fields
            if 'id' not in record:
                warnings.append(f"Record {i} missing 'id' field")
            
            # Check for empty values
            for key, value in record.items():
                if value == '' or value is None:
                    warnings.append(f"Record {i} has empty value for field '{key}'")
        
        return {
            'valid': len(warnings) == 0,
            'warnings': warnings
        }
    
    # ============================================================================
    # DATA LOADING
    # ============================================================================
    
    async def load_data(self, 
                       transformed_data: List[Dict[str, Any]],
                       destination_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load transformed data to destination."""
        try:
            logger.info(f"Loading {len(transformed_data)} records to destination")
            
            # Validate destination configuration
            if 'type' not in destination_config:
                raise ValueError("Destination configuration missing 'type' field")
            
            # Load data based on destination type
            if destination_config['type'] == 'database':
                result = await self._load_to_database(transformed_data, destination_config)
            elif destination_config['type'] == 'file':
                result = await self._load_to_file(transformed_data, destination_config)
            elif destination_config['type'] == 'api':
                result = await self._load_to_api(transformed_data, destination_config)
            else:
                raise ValueError(f"Unsupported destination type: {destination_config['type']}")
            
            # Log loading operation
            await self._log_data_loading(len(transformed_data), destination_config, result)
            
            logger.info(f"Successfully loaded {len(transformed_data)} records")
            return result
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            await self._log_loading_error(len(transformed_data), destination_config, str(e))
            raise
    
    async def _load_to_database(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to database."""
        # Simulate database loading
        await asyncio.sleep(0.8)
        
        # In a real implementation, this would insert data into the database
        # For now, we'll just simulate the operation
        
        return {
            'destination': 'database',
            'records_loaded': len(data),
            'success': True,
            'load_time': 0.8,
            'table': config.get('table', 'default_table')
        }
    
    async def _load_to_file(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to file."""
        # Simulate file writing
        await asyncio.sleep(0.3)
        
        file_path = config.get('path', '/tmp/data_export.json')
        file_format = config.get('format', 'json')
        
        # In a real implementation, this would write data to a file
        
        return {
            'destination': 'file',
            'records_loaded': len(data),
            'success': True,
            'load_time': 0.3,
            'file_path': file_path,
            'format': file_format
        }
    
    async def _load_to_api(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to external API."""
        # Simulate API call
        await asyncio.sleep(1.2)
        
        api_url = config.get('url', 'https://api.example.com/data')
        batch_size = config.get('batch_size', 100)
        
        # In a real implementation, this would send data to an external API
        
        return {
            'destination': 'api',
            'records_loaded': len(data),
            'success': True,
            'load_time': 1.2,
            'api_url': api_url,
            'batches_sent': (len(data) + batch_size - 1) // batch_size
        }
    
    # ============================================================================
    # END-TO-END PIPELINE EXECUTION
    # ============================================================================
    
    async def execute_pipeline(self, 
                             scraper_id: int,
                             data_type: str,
                             pipeline_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the complete data pipeline."""
        try:
            logger.info(f"Executing pipeline for scraper {scraper_id}, data type: {data_type}")
            
            start_time = datetime.utcnow()
            
            # Step 1: Extract
            logger.info("Step 1: Extracting data...")
            raw_data = await self.extract_data(scraper_id, data_type, pipeline_config.get('extraction'))
            
            # Step 2: Transform
            logger.info("Step 2: Transforming data...")
            transformed_data = await self.transform_data(raw_data, pipeline_config.get('transformation'))
            
            # Step 3: Load
            logger.info("Step 3: Loading data...")
            load_result = await self.load_data(transformed_data, pipeline_config.get('destination'))
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Prepare result
            result = {
                'success': True,
                'scraper_id': scraper_id,
                'data_type': data_type,
                'records_processed': len(raw_data),
                'execution_time': execution_time,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'extraction': {
                    'records_extracted': len(raw_data),
                    'success': True
                },
                'transformation': {
                    'records_transformed': len(transformed_data),
                    'success': True
                },
                'loading': load_result
            }
            
            # Log pipeline execution
            await self._log_pipeline_execution(scraper_id, data_type, result)
            
            logger.info(f"Pipeline execution completed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            
            # Log pipeline failure
            await self._log_pipeline_failure(scraper_id, data_type, str(e))
            
            return {
                'success': False,
                'scraper_id': scraper_id,
                'data_type': data_type,
                'error': str(e),
                'execution_time': 0,
                'start_time': datetime.utcnow().isoformat(),
                'end_time': datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # PIPELINE MONITORING AND LOGGING
    # ============================================================================
    
    async def _get_scraper_info(self, scraper_id: int) -> Optional[ScraperInfo]:
        """Get scraper information."""
        try:
            result = await self.db_session.execute(
                self.db_session.query(ScraperInfo).filter(ScraperInfo.id == scraper_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting scraper info: {e}")
            return None
    
    async def _log_extraction(self, scraper_id: int, data_type: str, record_count: int):
        """Log data extraction operation."""
        try:
            log_entry = ScraperLog(
                scraper_id=scraper_id,
                level='info',
                message=f"Extracted {record_count} {data_type} records",
                log_data=json.dumps({
                    'operation': 'extraction',
                    'data_type': data_type,
                    'record_count': record_count,
                    'timestamp': datetime.utcnow().isoformat()
                })
            )
            
            self.db_session.add(log_entry)
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log extraction: {e}")
    
    async def _log_extraction_error(self, scraper_id: int, data_type: str, error_message: str):
        """Log data extraction error."""
        try:
            log_entry = ScraperLog(
                scraper_id=scraper_id,
                level='error',
                message=f"Extraction failed for {data_type}: {error_message}",
                log_data=json.dumps({
                    'operation': 'extraction',
                    'data_type': data_type,
                    'error': error_message,
                    'timestamp': datetime.utcnow().isoformat()
                })
            )
            
            self.db_session.add(log_entry)
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log extraction error: {e}")
    
    async def _log_data_loading(self, record_count: int, destination_config: Dict[str, Any], result: Dict[str, Any]):
        """Log data loading operation."""
        try:
            # This would log to a general pipeline log in a real implementation
            logger.info(f"Data loading completed: {record_count} records to {destination_config.get('type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to log data loading: {e}")
    
    async def _log_loading_error(self, record_count: int, destination_config: Dict[str, Any], error_message: str):
        """Log data loading error."""
        try:
            # This would log to a general pipeline log in a real implementation
            logger.error(f"Data loading failed: {record_count} records to {destination_config.get('type', 'unknown')}: {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to log loading error: {e}")
    
    async def _log_pipeline_execution(self, scraper_id: int, data_type: str, result: Dict[str, Any]):
        """Log pipeline execution."""
        try:
            log_entry = ScraperLog(
                scraper_id=scraper_id,
                level='info',
                message=f"Pipeline executed successfully for {data_type}",
                log_data=json.dumps({
                    'operation': 'pipeline_execution',
                    'data_type': data_type,
                    'result': result,
                    'timestamp': datetime.utcnow().isoformat()
                })
            )
            
            self.db_session.add(log_entry)
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log pipeline execution: {e}")
    
    async def _log_pipeline_failure(self, scraper_id: int, data_type: str, error_message: str):
        """Log pipeline failure."""
        try:
            log_entry = ScraperLog(
                scraper_id=scraper_id,
                level='error',
                message=f"Pipeline failed for {data_type}: {error_message}",
                log_data=json.dumps({
                    'operation': 'pipeline_execution',
                    'data_type': data_type,
                    'error': error_message,
                    'timestamp': datetime.utcnow().isoformat()
                })
            )
            
            self.db_session.add(log_entry)
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log pipeline failure: {e}")

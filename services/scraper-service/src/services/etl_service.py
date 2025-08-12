"""
ETL Service for OpenPolicy Scraper Service

This module provides ETL (Extract, Transform, Load) service functionality
for processing and managing data workflows.
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


class ETLService:
    """Manages ETL operations and data workflows."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the ETL service."""
        self.db_session = db_session
        self.active_workflows: Dict[str, asyncio.Task] = {}
        self.etl_lock = asyncio.Lock()
        
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
    # ETL WORKFLOW MANAGEMENT
    # ============================================================================
    
    async def create_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """Create a new ETL workflow."""
        try:
            workflow_id = str(uuid4())
            
            # Validate workflow configuration
            validation_result = await self._validate_workflow_config(workflow_config)
            if not validation_result['valid']:
                raise ValueError(f"Invalid workflow configuration: {validation_result['errors']}")
            
            # Store workflow configuration
            workflow_data = {
                'id': workflow_id,
                'config': workflow_config,
                'status': 'created',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # In a real implementation, this would be stored in a database
            logger.info(f"Created ETL workflow: {workflow_id}")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def _validate_workflow_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow configuration."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['name', 'steps', 'schedule']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate steps
        if 'steps' in config:
            for i, step in enumerate(config['steps']):
                if 'type' not in step:
                    errors.append(f"Step {i} missing 'type' field")
                if 'name' not in step:
                    errors.append(f"Step {i} missing 'name' field")
                
                # Validate step-specific configuration
                step_type = step.get('type')
                if step_type == 'extract':
                    if 'source' not in step:
                        errors.append(f"Extract step {i} missing 'source' field")
                elif step_type == 'transform':
                    if 'rules' not in step:
                        warnings.append(f"Transform step {i} missing 'rules' field")
                elif step_type == 'load':
                    if 'destination' not in step:
                        errors.append(f"Load step {i} missing 'destination' field")
        
        # Validate schedule
        schedule = config.get('schedule')
        if schedule and schedule not in ['immediate', 'daily', 'weekly', 'monthly']:
            warnings.append("Schedule format may not be supported")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def execute_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an ETL workflow."""
        try:
            logger.info(f"Executing ETL workflow: {workflow_id}")
            
            start_time = datetime.utcnow()
            
            # Get workflow configuration (in real implementation, fetch from database)
            workflow_config = await self._get_workflow_config(workflow_id)
            if not workflow_config:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Execute workflow steps
            results = []
            for step in workflow_config['steps']:
                step_result = await self._execute_workflow_step(step, parameters or {})
                results.append(step_result)
                
                # Check if step failed
                if not step_result['success']:
                    logger.error(f"Workflow step failed: {step_result['error']}")
                    break
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Determine overall success
            overall_success = all(step['success'] for step in results)
            
            # Prepare result
            result = {
                'workflow_id': workflow_id,
                'success': overall_success,
                'execution_time': execution_time,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'steps': results,
                'parameters': parameters or {}
            }
            
            # Log workflow execution
            await self._log_workflow_execution(workflow_id, result)
            
            logger.info(f"ETL workflow {workflow_id} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"ETL workflow execution failed: {e}")
            
            # Log workflow failure
            await self._log_workflow_failure(workflow_id, str(e))
            
            return {
                'workflow_id': workflow_id,
                'success': False,
                'error': str(e),
                'execution_time': 0,
                'start_time': datetime.utcnow().isoformat(),
                'end_time': datetime.utcnow().isoformat()
            }
    
    async def _execute_workflow_step(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            step_start_time = datetime.utcnow()
            step_type = step['type']
            step_name = step['name']
            
            logger.info(f"Executing step: {step_name} ({step_type})")
            
            # Execute step based on type
            if step_type == 'extract':
                step_result = await self._execute_extract_step(step, parameters)
            elif step_type == 'transform':
                step_result = await self._execute_transform_step(step, parameters)
            elif step_type == 'load':
                step_result = await self._execute_load_step(step, parameters)
            else:
                step_result = await self._execute_custom_step(step, parameters)
            
            # Calculate step execution time
            step_end_time = datetime.utcnow()
            step_execution_time = (step_end_time - step_start_time).total_seconds()
            
            # Add metadata to step result
            step_result.update({
                'step_name': step_name,
                'step_type': step_type,
                'execution_time': step_execution_time,
                'start_time': step_start_time.isoformat(),
                'end_time': step_end_time.isoformat()
            })
            
            logger.info(f"Step {step_name} completed in {step_execution_time:.2f}s")
            return step_result
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {
                'step_name': step.get('name', 'unknown'),
                'step_type': step.get('type', 'unknown'),
                'success': False,
                'error': str(e),
                'execution_time': 0
            }
    
    async def _execute_extract_step(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an extract step."""
        try:
            source = step.get('source', {})
            source_type = source.get('type', 'database')
            
            if source_type == 'database':
                # Extract from database
                query = source.get('query')
                if not query:
                    raise ValueError("Database extract step missing 'query' field")
                
                # Simulate database extraction
                await asyncio.sleep(0.5)
                
                return {
                    'success': True,
                    'data_type': 'database',
                    'records_extracted': 100,
                    'query': query
                }
                
            elif source_type == 'file':
                # Extract from file
                file_path = source.get('path')
                if not file_path:
                    raise ValueError("File extract step missing 'path' field")
                
                # Simulate file extraction
                await asyncio.sleep(0.3)
                
                return {
                    'success': True,
                    'data_type': 'file',
                    'records_extracted': 50,
                    'file_path': file_path
                }
                
            elif source_type == 'api':
                # Extract from API
                api_url = source.get('url')
                if not api_url:
                    raise ValueError("API extract step missing 'url' field")
                
                # Simulate API extraction
                await asyncio.sleep(0.8)
                
                return {
                    'success': True,
                    'data_type': 'api',
                    'records_extracted': 75,
                    'api_url': api_url
                }
                
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
                
        except Exception as e:
            logger.error(f"Extract step failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_transform_step(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a transform step."""
        try:
            rules = step.get('rules', [])
            
            # Simulate transformation
            await asyncio.sleep(0.4)
            
            # Apply transformation rules
            transformations_applied = len(rules)
            
            return {
                'success': True,
                'data_type': 'transformed',
                'transformations_applied': transformations_applied,
                'rules': rules
            }
            
        except Exception as e:
            logger.error(f"Transform step failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_load_step(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a load step."""
        try:
            destination = step.get('destination', {})
            dest_type = destination.get('type', 'database')
            
            if dest_type == 'database':
                # Load to database
                table = destination.get('table')
                if not table:
                    raise ValueError("Database load step missing 'table' field")
                
                # Simulate database loading
                await asyncio.sleep(0.6)
                
                return {
                    'success': True,
                    'data_type': 'database',
                    'records_loaded': 100,
                    'table': table
                }
                
            elif dest_type == 'file':
                # Load to file
                file_path = destination.get('path')
                if not file_path:
                    raise ValueError("File load step missing 'path' field")
                
                # Simulate file writing
                await asyncio.sleep(0.2)
                
                return {
                    'success': True,
                    'data_type': 'file',
                    'records_loaded': 100,
                    'file_path': file_path
                }
                
            elif dest_type == 'api':
                # Load to API
                api_url = destination.get('url')
                if not api_url:
                    raise ValueError("API load step missing 'url' field")
                
                # Simulate API call
                await asyncio.sleep(1.0)
                
                return {
                    'success': True,
                    'data_type': 'api',
                    'records_loaded': 100,
                    'api_url': api_url
                }
                
            else:
                raise ValueError(f"Unsupported destination type: {dest_type}")
                
        except Exception as e:
            logger.error(f"Load step failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_custom_step(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a custom step."""
        try:
            # Simulate custom step execution
            await asyncio.sleep(0.3)
            
            return {
                'success': True,
                'data_type': 'custom',
                'custom_config': step.get('config', {})
            }
            
        except Exception as e:
            logger.error(f"Custom step failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ============================================================================
    # WORKFLOW SCHEDULING
    # ============================================================================
    
    async def schedule_workflow(self, workflow_id: str, schedule: str, parameters: Dict[str, Any] = None) -> bool:
        """Schedule a workflow for execution."""
        try:
            logger.info(f"Scheduling workflow {workflow_id} with schedule: {schedule}")
            
            # Validate schedule
            if schedule not in ['immediate', 'daily', 'weekly', 'monthly']:
                raise ValueError(f"Unsupported schedule: {schedule}")
            
            # Store schedule information
            schedule_data = {
                'workflow_id': workflow_id,
                'schedule': schedule,
                'parameters': parameters or {},
                'next_run': self._calculate_next_run(schedule),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # In a real implementation, this would be stored in a database
            logger.info(f"Workflow {workflow_id} scheduled for {schedule}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule workflow: {e}")
            return False
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time based on schedule."""
        now = datetime.utcnow()
        
        if schedule == 'immediate':
            return now
        elif schedule == 'daily':
            return now + timedelta(days=1)
        elif schedule == 'weekly':
            return now + timedelta(weeks=1)
        elif schedule == 'monthly':
            # Simple monthly calculation (30 days)
            return now + timedelta(days=30)
        else:
            return now
    
    async def get_scheduled_workflows(self) -> List[Dict[str, Any]]:
        """Get all scheduled workflows."""
        try:
            # In a real implementation, this would fetch from database
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to get scheduled workflows: {e}")
            return []
    
    # ============================================================================
    # WORKFLOW MONITORING
    # ============================================================================
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow."""
        try:
            # In a real implementation, this would fetch from database
            # For now, return a default status
            return {
                'workflow_id': workflow_id,
                'status': 'unknown',
                'last_run': None,
                'next_run': None,
                'execution_count': 0,
                'success_count': 0,
                'failure_count': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return None
    
    async def get_workflow_history(self, workflow_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history of a workflow."""
        try:
            # In a real implementation, this would fetch from database
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to get workflow history: {e}")
            return []
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        try:
            logger.info(f"Cancelling workflow: {workflow_id}")
            
            # Check if workflow is running
            if workflow_id in self.active_workflows:
                task = self.active_workflows[workflow_id]
                task.cancel()
                del self.active_workflows[workflow_id]
                logger.info(f"Workflow {workflow_id} cancelled")
                return True
            else:
                logger.info(f"Workflow {workflow_id} not running")
                return True
                
        except Exception as e:
            logger.error(f"Failed to cancel workflow: {e}")
            return False
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def _get_workflow_config(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow configuration."""
        try:
            # In a real implementation, this would fetch from database
            # For now, return a sample configuration
            return {
                'id': workflow_id,
                'name': f'Workflow {workflow_id}',
                'steps': [
                    {
                        'type': 'extract',
                        'name': 'Extract Data',
                        'source': {
                            'type': 'database',
                            'query': 'SELECT * FROM source_table'
                        }
                    },
                    {
                        'type': 'transform',
                        'name': 'Transform Data',
                        'rules': [
                            'clean_whitespace',
                            'validate_required_fields',
                            'convert_data_types'
                        ]
                    },
                    {
                        'type': 'load',
                        'name': 'Load Data',
                        'destination': {
                            'type': 'database',
                            'table': 'target_table'
                        }
                    }
                ],
                'schedule': 'daily'
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow config: {e}")
            return None
    
    async def _log_workflow_execution(self, workflow_id: str, result: Dict[str, Any]):
        """Log workflow execution."""
        try:
            # In a real implementation, this would log to database
            logger.info(f"Workflow {workflow_id} execution logged")
            
        except Exception as e:
            logger.error(f"Failed to log workflow execution: {e}")
    
    async def _log_workflow_failure(self, workflow_id: str, error_message: str):
        """Log workflow failure."""
        try:
            # In a real implementation, this would log to database
            logger.error(f"Workflow {workflow_id} failure logged: {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to log workflow failure: {e}")
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the ETL service."""
        try:
            # Check database connection
            db_healthy = True
            try:
                await self.db_session.execute("SELECT 1")
            except Exception:
                db_healthy = False
            
            # Check active workflows
            active_workflows_count = len(self.active_workflows)
            
            return {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'database': 'connected' if db_healthy else 'disconnected',
                'active_workflows': active_workflows_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

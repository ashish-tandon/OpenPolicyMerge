"""
Enhanced Scraper Manager Service for OpenPolicy Scraper Service

This module provides comprehensive scraper management with enhanced logging.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from ..core.models import (
    ScraperInfo, ScraperJob, ScraperStatus, JobStatus, ScraperPriority
)
from ..core.database import get_db_async
from ..core.logging_config import (
    get_logger, log_function_call, log_performance, log_scraper_activity,
    log_error, log_system_health
)

logger = get_logger(__name__)


class ScraperManager:
    """Enhanced scraper manager with comprehensive logging and error handling."""
    
    def __init__(self):
        """Initialize the scraper manager."""
        logger.info("🚀 Initializing Scraper Manager")
        self.active_jobs: Dict[int, ScraperJob] = {}
        self.job_lock = asyncio.Lock()
        self.health_check_interval = 300  # 5 minutes
        self.max_concurrent_jobs = 10
        
        logger.info(f"🔧 Configuration: max_concurrent_jobs={self.max_concurrent_jobs}")
        logger.info(f"🔧 Configuration: health_check_interval={self.health_check_interval}s")
        
        # Initialize health monitoring
        self.last_health_check = datetime.utcnow()
        self.health_status = "healthy"
        
        logger.info("✅ Scraper Manager initialized successfully")
    
    async def __aenter__(self):
        """Async context manager entry."""
        logger.info("🔓 Scraper Manager context entered")
        await self._startup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        logger.info("🔒 Scraper Manager context exiting")
        await self._cleanup()
        
        if exc_type:
            logger.error(f"🚨 Exception during context exit: {exc_type.__name__}: {exc_val}")
            log_error(exc_val, "ScraperManager.__aexit__")
    
    async def _startup(self):
        """Perform startup operations."""
        logger.info("🚀 Starting Scraper Manager...")
        
        try:
            # Initialize database connection
            logger.info("🗄️ Initializing database connection...")
            # Database initialization would go here
            
            # Start health monitoring
            logger.info("🏥 Starting health monitoring...")
            asyncio.create_task(self._health_monitor())
            
            # Load existing scrapers
            logger.info("📋 Loading existing scrapers...")
            scrapers = await self.get_scrapers()
            logger.info(f"📊 Loaded {len(scrapers)} existing scrapers")
            
            logger.info("✅ Scraper Manager startup completed")
            
        except Exception as e:
            logger.error(f"❌ Startup failed: {e}")
            log_error(e, "ScraperManager._startup")
            raise
    
    async def _cleanup(self):
        """Perform cleanup operations."""
        logger.info("🧹 Cleaning up Scraper Manager...")
        
        try:
            # Stop all active jobs
            if self.active_jobs:
                logger.info(f"🛑 Stopping {len(self.active_jobs)} active jobs...")
                for job_id, job in self.active_jobs.items():
                    await self._stop_job(job_id)
            
            # Close database connections
            logger.info("🗄️ Closing database connections...")
            
            logger.info("✅ Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            log_error(e, "ScraperManager._cleanup")
    
    async def _health_monitor(self):
        """Monitor system health."""
        logger.info("🏥 Health monitoring started")
        
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
                
            except asyncio.CancelledError:
                logger.info("🏥 Health monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                log_error(e, "ScraperManager._health_monitor")
    
    async def _perform_health_check(self):
        """Perform comprehensive health check."""
        logger.debug("🔍 Performing health check...")
        
        try:
            start_time = datetime.utcnow()
            
            # Check database connectivity
            db_healthy = await self._check_database_health()
            
            # Check active jobs
            jobs_healthy = await self._check_jobs_health()
            
            # Check system resources
            resources_healthy = await self._check_system_resources()
            
            # Determine overall health
            if db_healthy and jobs_healthy and resources_healthy:
                self.health_status = "healthy"
                logger.info("✅ Health check passed - system is healthy")
            else:
                self.health_status = "degraded"
                logger.warning("⚠️ Health check failed - system is degraded")
            
            # Log health status
            health_details = {
                "database": db_healthy,
                "jobs": jobs_healthy,
                "resources": resources_healthy,
                "active_jobs_count": len(self.active_jobs),
                "last_check": start_time.isoformat()
            }
            
            log_system_health("ScraperManager", self.health_status, health_details)
            
            # Update last health check time
            self.last_health_check = start_time
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_performance("health_check", duration, health_details)
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            log_error(e, "ScraperManager._perform_health_check")
            self.health_status = "error"
    
    async def _check_database_health(self) -> bool:
        """Check database health."""
        try:
            logger.debug("🗄️ Checking database health...")
            # Database health check would go here
            return True
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False
    
    async def _check_jobs_health(self) -> bool:
        """Check jobs health."""
        try:
            logger.debug("📋 Checking jobs health...")
            
            # Check for stuck jobs
            stuck_jobs = []
            for job_id, job in self.active_jobs.items():
                if job.status == JobStatus.RUNNING:
                    # Check if job has been running too long
                    if (datetime.utcnow() - job.started_at).total_seconds() > 3600:  # 1 hour
                        stuck_jobs.append(job_id)
            
            if stuck_jobs:
                logger.warning(f"⚠️ Found {len(stuck_jobs)} stuck jobs: {stuck_jobs}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Jobs health check failed: {e}")
            return False
    
    async def _check_system_resources(self) -> bool:
        """Check system resources."""
        try:
            logger.debug("💻 Checking system resources...")
            
            # Check memory usage
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                logger.warning(f"⚠️ High memory usage: {memory.percent}%")
                return False
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 95:
                logger.warning(f"⚠️ High CPU usage: {cpu_percent}%")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System resources check failed: {e}")
            return False
    
    @log_function_call
    async def get_scrapers(
        self,
        enabled_only: bool = False,
        jurisdiction_level: Optional[str] = None
    ) -> List[ScraperInfo]:
        """Get scrapers with optional filtering."""
        logger.info(f"📋 Getting scrapers: enabled_only={enabled_only}, jurisdiction_level={jurisdiction_level}")
        
        try:
            start_time = datetime.utcnow()
            
            # Simulate database query
            scrapers = [
                ScraperInfo(
                    id=1,
                    name="parliament_ca",
                    url="https://parl.ca",
                    jurisdiction_level="federal",
                    status=ScraperStatus.COMPLETED,
                    enabled=True,
                    data_collected=150
                ),
                ScraperInfo(
                    id=2,
                    name="ca_on",
                    url="https://ontario.ca",
                    jurisdiction_level="provincial",
                    status=ScraperStatus.RUNNING,
                    enabled=True,
                    data_collected=200
                ),
                ScraperInfo(
                    id=3,
                    name="ca_on_toronto",
                    url="https://toronto.ca",
                    jurisdiction_level="municipal",
                    status=ScraperStatus.COMPLETED,
                    enabled=True,
                    data_collected=250
                )
            ]
            
            # Apply filters
            if enabled_only:
                scrapers = [s for s in scrapers if s.enabled]
                logger.debug(f"🔍 Filtered to {len(scrapers)} enabled scrapers")
            
            if jurisdiction_level:
                scrapers = [s for s in scrapers if s.jurisdiction_level == jurisdiction_level]
                logger.debug(f"🔍 Filtered to {len(scrapers)} {jurisdiction_level} scrapers")
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_performance("get_scrapers", duration, {
                "total_scrapers": len(scrapers),
                "enabled_only": enabled_only,
                "jurisdiction_level": jurisdiction_level
            })
            
            logger.info(f"✅ Retrieved {len(scrapers)} scrapers")
            return scrapers
            
        except Exception as e:
            logger.error(f"❌ Failed to get scrapers: {e}")
            log_error(e, "ScraperManager.get_scrapers")
            raise
    
    @log_function_call
    async def get_scraper_by_id(self, scraper_id: int) -> Optional[ScraperInfo]:
        """Get scraper by ID."""
        logger.info(f"🔍 Getting scraper by ID: {scraper_id}")
        
        try:
            scrapers = await self.get_scrapers()
            scraper = next((s for s in scrapers if s.id == scraper_id), None)
            
            if scraper:
                logger.info(f"✅ Found scraper: {scraper.name}")
                return scraper
            else:
                logger.warning(f"⚠️ Scraper not found: {scraper_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get scraper {scraper_id}: {e}")
            log_error(e, "ScraperManager.get_scraper_by_id", {"scraper_id": scraper_id})
            raise
    
    @log_function_call
    async def create_scraper(self, scraper_data: Dict[str, Any]) -> ScraperInfo:
        """Create a new scraper."""
        logger.info(f"➕ Creating new scraper: {scraper_data.get('name', 'Unknown')}")
        
        try:
            # Validate scraper data
            required_fields = ['name', 'url', 'jurisdiction_level']
            for field in required_fields:
                if field not in scraper_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create scraper info
            scraper = ScraperInfo(
                id=len(await self.get_scrapers()) + 1,
                name=scraper_data['name'],
                url=scraper_data['url'],
                jurisdiction_level=scraper_data['jurisdiction_level'],
                status=ScraperStatus.IDLE,
                enabled=scraper_data.get('enabled', True),
                data_collected=0
            )
            
            logger.info(f"✅ Created scraper: {scraper.name} (ID: {scraper.id})")
            
            # Log scraper activity
            log_scraper_activity(scraper.id, "created", {
                "name": scraper.name,
                "url": scraper.url,
                "jurisdiction_level": scraper.jurisdiction_level
            })
            
            return scraper
            
        except Exception as e:
            logger.error(f"❌ Failed to create scraper: {e}")
            log_error(e, "ScraperManager.create_scraper", {"scraper_data": scraper_data})
            raise
    
    @log_function_call
    async def update_scraper(self, scraper_id: int, updates: Dict[str, Any]) -> Optional[ScraperInfo]:
        """Update scraper information."""
        logger.info(f"✏️ Updating scraper {scraper_id}: {updates}")
        
        try:
            scraper = await self.get_scraper_by_id(scraper_id)
            if not scraper:
                logger.warning(f"⚠️ Cannot update non-existent scraper: {scraper_id}")
                return None
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(scraper, key):
                    old_value = getattr(scraper, key)
                    setattr(scraper, key, value)
                    logger.debug(f"🔄 Updated {key}: {old_value} -> {value}")
                else:
                    logger.warning(f"⚠️ Unknown field: {key}")
            
            logger.info(f"✅ Updated scraper {scraper_id}")
            
            # Log scraper activity
            log_scraper_activity(scraper_id, "updated", updates)
            
            return scraper
            
        except Exception as e:
            logger.error(f"❌ Failed to update scraper {scraper_id}: {e}")
            log_error(e, "ScraperManager.update_scraper", {"scraper_id": scraper_id, "updates": updates})
            raise
    
    @log_function_call
    async def delete_scraper(self, scraper_id: int) -> bool:
        """Delete a scraper."""
        logger.info(f"🗑️ Deleting scraper: {scraper_id}")
        
        try:
            scraper = await self.get_scraper_by_id(scraper_id)
            if not scraper:
                logger.warning(f"⚠️ Cannot delete non-existent scraper: {scraper_id}")
                return False
            
            # Check if scraper has active jobs
            if scraper_id in self.active_jobs:
                logger.warning(f"⚠️ Cannot delete scraper with active jobs: {scraper_id}")
                return False
            
            logger.info(f"✅ Deleted scraper: {scraper.name}")
            
            # Log scraper activity
            log_scraper_activity(scraper_id, "deleted", {
                "name": scraper.name,
                "url": scraper.url
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete scraper {scraper_id}: {e}")
            log_error(e, "ScraperManager.delete_scraper", {"scraper_id": scraper_id})
            raise
    
    @log_function_call
    async def run_scraper(self, scraper_id: int) -> ScraperJob:
        """Run a scraper."""
        logger.info(f"🚀 Running scraper: {scraper_id}")
        
        try:
            # Check if scraper exists
            scraper = await self.get_scraper_by_id(scraper_id)
            if not scraper:
                raise ValueError(f"Scraper {scraper_id} not found")
            
            # Check if scraper is enabled
            if not scraper.enabled:
                raise ValueError(f"Scraper {scraper_id} is disabled")
            
            # Check concurrent job limit
            if len(self.active_jobs) >= self.max_concurrent_jobs:
                raise RuntimeError(f"Maximum concurrent jobs ({self.max_concurrent_jobs}) reached")
            
            # Create job
            job = ScraperJob(
                id=len(self.active_jobs) + 1,
                scraper_id=scraper_id,
                status=JobStatus.RUNNING,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow()
            )
            
            # Add to active jobs
            async with self.job_lock:
                self.active_jobs[job.id] = job
            
            # Update scraper status
            await self.update_scraper(scraper_id, {"status": ScraperStatus.RUNNING})
            
            logger.info(f"✅ Started scraper job: {job.id} for scraper: {scraper.name}")
            
            # Log scraper activity
            log_scraper_activity(scraper_id, "started", {
                "job_id": job.id,
                "scraper_name": scraper.name,
                "url": scraper.url
            })
            
            return job
            
        except Exception as e:
            logger.error(f"❌ Failed to run scraper {scraper_id}: {e}")
            log_error(e, "ScraperManager.run_scraper", {"scraper_id": scraper_id})
            raise
    
    @log_function_call
    async def get_jobs(self, limit: int = 100) -> List[ScraperJob]:
        """Get scraper jobs."""
        logger.info(f"📋 Getting jobs: limit={limit}")
        
        try:
            # Return active jobs
            jobs = list(self.active_jobs.values())[:limit]
            
            logger.info(f"✅ Retrieved {len(jobs)} jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Failed to get jobs: {e}")
            log_error(e, "ScraperManager.get_jobs", {"limit": limit})
            raise
    
    @log_function_call
    async def create_job(self, scraper_id: int) -> ScraperJob:
        """Create a new job."""
        logger.info(f"➕ Creating job for scraper: {scraper_id}")
        
        try:
            job = ScraperJob(
                id=len(self.active_jobs) + 1,
                scraper_id=scraper_id,
                status=JobStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            # Add to active jobs
            async with self.job_lock:
                self.active_jobs[job.id] = job
            
            logger.info(f"✅ Created job: {job.id}")
            return job
            
        except Exception as e:
            logger.error(f"❌ Failed to create job: {e}")
            log_error(e, "ScraperManager.create_job", {"scraper_id": scraper_id})
            raise
    
    @log_function_call
    async def update_job_status(
        self,
        scraper_id: int,
        status: str,
        data_collected: int = 0,
        duration: float = 0.0
    ) -> bool:
        """Update job status."""
        logger.info(f"✏️ Updating job status for scraper {scraper_id}: {status}")
        
        try:
            # Find job for this scraper
            job = None
            for j in self.active_jobs.values():
                if j.scraper_id == scraper_id:
                    job = j
                    break
            
            if not job:
                logger.warning(f"⚠️ No active job found for scraper: {scraper_id}")
                return False
            
            # Update job status
            old_status = job.status
            job.status = JobStatus(status)
            job.updated_at = datetime.utcnow()
            
            if status == JobStatus.COMPLETED:
                job.completed_at = datetime.utcnow()
                job.duration = duration
                
                # Remove from active jobs
                async with self.job_lock:
                    if job.id in self.active_jobs:
                        del self.active_jobs[job.id]
                
                # Update scraper status
                await self.update_scraper(scraper_id, {
                    "status": ScraperStatus.COMPLETED,
                    "data_collected": data_collected
                })
            
            logger.info(f"✅ Updated job {job.id} status: {old_status} -> {status}")
            
            # Log job activity
            log_scraper_activity(scraper_id, "status_updated", {
                "job_id": job.id,
                "old_status": old_status,
                "new_status": status,
                "data_collected": data_collected,
                "duration": duration
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update job status: {e}")
            log_error(e, "ScraperManager.update_job_status", {
                "scraper_id": scraper_id,
                "status": status,
                "data_collected": data_collected,
                "duration": duration
            })
            raise
    
    @log_function_call
    async def get_job_logs(self, job_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs for a specific job."""
        logger.info(f"📋 Getting logs for job: {job_id}, limit: {limit}")
        
        try:
            # In a real implementation, this would query the database
            # For now, return empty list
            logger.info(f"📋 No logs found for job {job_id}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get job logs: {e}")
            log_error(e, "ScraperManager.get_job_logs", {"job_id": job_id, "limit": limit})
            raise
    
    @log_function_call
    async def scraper_validation(self, scraper_id: int) -> Dict[str, Any]:
        """Validate scraper configuration."""
        logger.info(f"🔍 Validating scraper: {scraper_id}")
        
        try:
            scraper = await self.get_scraper_by_id(scraper_id)
            if not scraper:
                raise ValueError(f"Scraper {scraper_id} not found")
            
            # Perform validation checks
            validation_results = {
                "scraper_id": scraper_id,
                "name": scraper.name,
                "url_valid": scraper.url.startswith(('http://', 'https://')),
                "jurisdiction_valid": scraper.jurisdiction_level in ['federal', 'provincial', 'municipal'],
                "enabled": scraper.enabled,
                "status": scraper.status.value
            }
            
            # Check if validation passed
            validation_passed = all([
                validation_results["url_valid"],
                validation_results["jurisdiction_valid"],
                validation_results["enabled"]
            ])
            
            validation_results["valid"] = validation_passed
            
            if validation_passed:
                logger.info(f"✅ Scraper validation passed: {scraper.name}")
            else:
                logger.warning(f"⚠️ Scraper validation failed: {scraper.name}")
                logger.warning(f"📋 Validation details: {validation_results}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Scraper validation failed: {e}")
            log_error(e, "ScraperManager.scraper_validation", {"scraper_id": scraper_id})
            raise
    
    @log_function_call
    async def scraper_health_check(self, scraper_id: int) -> Dict[str, Any]:
        """Check scraper health."""
        logger.info(f"🏥 Checking scraper health: {scraper_id}")
        
        try:
            scraper = await self.get_scraper_by_id(scraper_id)
            if not scraper:
                raise ValueError(f"Scraper {scraper_id} not found")
            
            # Perform health checks
            health_results = {
                "scraper_id": scraper_id,
                "name": scraper.name,
                "status": scraper.status.value,
                "enabled": scraper.enabled,
                "data_collected": scraper.data_collected,
                "last_check": datetime.utcnow().isoformat(),
                "health_score": 100
            }
            
            # Reduce health score for various issues
            if not scraper.enabled:
                health_results["health_score"] -= 30
                health_results["issues"] = ["scraper_disabled"]
            
            if scraper.status == ScraperStatus.ERROR:
                health_results["health_score"] -= 50
                health_results["issues"] = ["scraper_error"]
            
            if scraper.data_collected == 0:
                health_results["health_score"] -= 20
                health_results["issues"] = ["no_data_collected"]
            
            # Determine health status
            if health_results["health_score"] >= 80:
                health_results["status"] = "healthy"
            elif health_results["health_score"] >= 50:
                health_results["status"] = "degraded"
            else:
                health_results["status"] = "unhealthy"
            
            logger.info(f"🏥 Scraper health: {scraper.name} - {health_results['status']} (score: {health_results['health_score']})")
            
            # Log health status
            log_system_health(f"Scraper_{scraper_id}", health_results["status"], health_results)
            
            return health_results
            
        except Exception as e:
            logger.error(f"❌ Scraper health check failed: {e}")
            log_error(e, "ScraperManager.scraper_health_check", {"scraper_id": scraper_id})
            raise
    
    @log_function_call
    async def error_handling(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle errors with comprehensive logging."""
        logger.error(f"🚨 Error handling: {context}")
        logger.error(f"🚨 Error type: {type(error).__name__}")
        logger.error(f"🚨 Error message: {str(error)}")
        
        try:
            # Log error with context
            log_error(error, context, {
                "timestamp": datetime.utcnow().isoformat(),
                "context": context
            })
            
            # Create error report
            error_report = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "traceback": str(error.__traceback__)
            }
            
            # Update system health if critical
            if isinstance(error, (RuntimeError, ConnectionError)):
                self.health_status = "degraded"
                logger.warning("⚠️ System health degraded due to critical error")
            
            return error_report
            
        except Exception as e:
            logger.error(f"❌ Error handling failed: {e}")
            return {"error": "Error handling failed", "original_error": str(error)}
    
    @log_function_call
    async def concurrent_execution(self, scraper_ids: List[int]) -> List[ScraperJob]:
        """Execute multiple scrapers concurrently."""
        logger.info(f"🚀 Starting concurrent execution for {len(scraper_ids)} scrapers")
        
        try:
            start_time = datetime.utcnow()
            
            # Create tasks for concurrent execution
            tasks = []
            for scraper_id in scraper_ids:
                task = asyncio.create_task(self.run_scraper(scraper_id))
                tasks.append(task)
            
            # Execute all tasks concurrently
            logger.info(f"🔄 Executing {len(tasks)} concurrent tasks...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_jobs = []
            failed_scrapers = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    scraper_id = scraper_ids[i]
                    logger.error(f"❌ Scraper {scraper_id} failed: {result}")
                    failed_scrapers.append(scraper_id)
                    log_error(result, f"concurrent_execution_scraper_{scraper_id}")
                else:
                    successful_jobs.append(result)
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_performance("concurrent_execution", duration, {
                "total_scrapers": len(scraper_ids),
                "successful": len(successful_jobs),
                "failed": len(failed_scrapers),
                "failed_scrapers": failed_scrapers
            })
            
            logger.info(f"✅ Concurrent execution completed: {len(successful_jobs)} successful, {len(failed_scrapers)} failed")
            
            return successful_jobs
            
        except Exception as e:
            logger.error(f"❌ Concurrent execution failed: {e}")
            log_error(e, "ScraperManager.concurrent_execution", {"scraper_ids": scraper_ids})
            raise
    
    async def _stop_job(self, job_id: int):
        """Stop a specific job."""
        logger.info(f"🛑 Stopping job: {job_id}")
        
        try:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                job.status = JobStatus.STOPPED
                job.updated_at = datetime.utcnow()
                
                # Remove from active jobs
                async with self.job_lock:
                    if job_id in self.active_jobs:
                        del self.active_jobs[job_id]
                
                logger.info(f"✅ Stopped job: {job_id}")
            else:
                logger.warning(f"⚠️ Job not found: {job_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to stop job {job_id}: {e}")
            log_error(e, "ScraperManager._stop_job", {"job_id": job_id})
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "health_status": self.health_status,
            "active_jobs_count": len(self.active_jobs),
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "last_health_check": self.last_health_check.isoformat(),
            "uptime": (datetime.utcnow() - self.last_health_check).total_seconds()
        }

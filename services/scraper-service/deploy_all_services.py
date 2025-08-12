#!/usr/bin/env python3
"""
Comprehensive Service Deployment Script for OpenPolicy Scraper Service

This script deploys all services with enhanced logging and monitoring.
"""

import asyncio
import logging
import sys
import time
import signal
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import json

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import services
from src.services.scraper_manager import ScraperManager
from src.services.data_pipeline import DataPipeline
from src.services.etl_service import ETLService
from src.services.performance_monitor import PerformanceMonitor
from src.services.coverage_validator import CoverageValidator

# Import logging configuration
from src.core.logging_config import (
    setup_logging, get_logger, log_performance, log_system_health,
    log_error, log_scraper_activity, log_etl_operation
)

# Global variables for service management
services = {}
shutdown_event = asyncio.Event()
startup_time = None

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger = logging.getLogger('deployment')
    logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class ServiceDeploymentManager:
    """Manages the deployment of all services."""
    
    def __init__(self):
        """Initialize the deployment manager."""
        self.logger = get_logger(__name__)
        self.services_status = {}
        self.deployment_start_time = None
        self.health_check_interval = 30  # 30 seconds
        
        self.logger.info("🚀 Initializing Service Deployment Manager")
    
    async def deploy_all_services(self):
        """Deploy all services with comprehensive logging."""
        self.logger.info("🚀 Starting deployment of all services...")
        self.deployment_start_time = datetime.utcnow()
        
        try:
            # Step 1: Initialize logging system
            await self._initialize_logging()
            
            # Step 2: Deploy core services
            await self._deploy_core_services()
            
            # Step 3: Start health monitoring
            await self._start_health_monitoring()
            
            # Step 4: Run initial tests
            await self._run_initial_tests()
            
            # Step 5: Start service monitoring
            await self._start_service_monitoring()
            
            self.logger.info("✅ All services deployed successfully!")
            
            # Keep services running until shutdown
            await self._run_services()
            
        except Exception as e:
            self.logger.error(f"❌ Service deployment failed: {e}")
            log_error(e, "ServiceDeploymentManager.deploy_all_services")
            raise
    
    async def _initialize_logging(self):
        """Initialize the enhanced logging system."""
        self.logger.info("📝 Initializing enhanced logging system...")
        
        try:
            # Setup comprehensive logging
            loggers = setup_logging(
                log_level="DEBUG",
                enable_console=True,
                enable_file=True,
                enable_structured=True
            )
            
            self.logger.info(f"✅ Logging system initialized with {len(loggers)} loggers")
            
            # Test logging
            test_logger = logging.getLogger('deployment.test')
            test_logger.info("🧪 Logging system test successful")
            
        except Exception as e:
            self.logger.error(f"❌ Logging initialization failed: {e}")
            raise
    
    async def _deploy_core_services(self):
        """Deploy all core services."""
        self.logger.info("⚙️ Deploying core services...")
        
        try:
            # Deploy Scraper Manager
            self.logger.info("🕷️ Deploying Scraper Manager...")
            scraper_manager = ScraperManager()
            await scraper_manager.__aenter__()
            services['scraper_manager'] = scraper_manager
            self.services_status['scraper_manager'] = 'deployed'
            self.logger.info("✅ Scraper Manager deployed")
            
            # Deploy Data Pipeline
            self.logger.info("🔄 Deploying Data Pipeline...")
            data_pipeline = DataPipeline()
            await data_pipeline.__aenter__()
            services['data_pipeline'] = data_pipeline
            self.services_status['data_pipeline'] = 'deployed'
            self.logger.info("✅ Data Pipeline deployed")
            
            # Deploy ETL Service
            self.logger.info("⚙️ Deploying ETL Service...")
            etl_service = ETLService()
            await etl_service.__aenter__()
            services['etl_service'] = etl_service
            self.services_status['etl_service'] = 'deployed'
            self.logger.info("✅ ETL Service deployed")
            
            # Deploy Performance Monitor
            self.logger.info("📊 Deploying Performance Monitor...")
            performance_monitor = PerformanceMonitor()
            services['performance_monitor'] = performance_monitor
            self.services_status['performance_monitor'] = 'deployed'
            self.logger.info("✅ Performance Monitor deployed")
            
            # Deploy Coverage Validator
            self.logger.info("📋 Deploying Coverage Validator...")
            coverage_validator = CoverageValidator()
            services['coverage_validator'] = coverage_validator
            self.services_status['coverage_validator'] = 'deployed'
            self.logger.info("✅ Coverage Validator deployed")
            
            self.logger.info(f"✅ All {len(services)} core services deployed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Core services deployment failed: {e}")
            log_error(e, "ServiceDeploymentManager._deploy_core_services")
            raise
    
    async def _start_health_monitoring(self):
        """Start health monitoring for all services."""
        self.logger.info("🏥 Starting health monitoring...")
        
        try:
            # Start health monitoring task
            asyncio.create_task(self._health_monitor())
            self.logger.info("✅ Health monitoring started")
            
        except Exception as e:
            self.logger.error(f"❌ Health monitoring startup failed: {e}")
            log_error(e, "ServiceDeploymentManager._start_health_monitoring")
    
    async def _health_monitor(self):
        """Monitor health of all services."""
        self.logger.info("🏥 Health monitoring active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
                
            except asyncio.CancelledError:
                self.logger.info("🏥 Health monitoring cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Health monitoring error: {e}")
                log_error(e, "ServiceDeploymentManager._health_monitor")
    
    async def _perform_health_check(self):
        """Perform comprehensive health check of all services."""
        self.logger.debug("🔍 Performing comprehensive health check...")
        
        try:
            start_time = datetime.utcnow()
            health_results = {}
            
            # Check Scraper Manager health
            if 'scraper_manager' in services:
                try:
                    scraper_status = services['scraper_manager'].get_system_status()
                    health_results['scraper_manager'] = {
                        'status': scraper_status['health_status'],
                        'active_jobs': scraper_status['active_jobs_count'],
                        'max_jobs': scraper_status['max_concurrent_jobs']
                    }
                except Exception as e:
                    health_results['scraper_manager'] = {'status': 'error', 'error': str(e)}
            
            # Check Performance Monitor health
            if 'performance_monitor' in services:
                try:
                    perf_metrics = services['performance_monitor'].get_system_metrics()
                    health_results['performance_monitor'] = {
                        'status': 'healthy',
                        'metrics_count': len(perf_metrics) if perf_metrics else 0
                    }
                except Exception as e:
                    health_results['performance_monitor'] = {'status': 'error', 'error': str(e)}
            
            # Check Coverage Validator health
            if 'coverage_validator' in services:
                try:
                    coverage_data = services['coverage_validator'].measure_coverage('src')
                    health_results['coverage_validator'] = {
                        'status': 'healthy',
                        'coverage': coverage_data.get('coverage_percentage', 0)
                    }
                except Exception as e:
                    health_results['coverage_validator'] = {'status': 'error', 'error': str(e)}
            
            # Determine overall health
            healthy_services = sum(1 for s in health_results.values() if s.get('status') == 'healthy')
            total_services = len(health_results)
            
            if healthy_services == total_services:
                overall_status = "healthy"
            elif healthy_services > total_services // 2:
                overall_status = "degraded"
            else:
                overall_status = "unhealthy"
            
            # Log health status
            health_summary = {
                "overall_status": overall_status,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "services": health_results,
                "timestamp": start_time.isoformat()
            }
            
            log_system_health("AllServices", overall_status, health_summary)
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_performance("comprehensive_health_check", duration, health_summary)
            
            self.logger.info(f"🏥 Health check completed: {overall_status} ({healthy_services}/{total_services} services healthy)")
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            log_error(e, "ServiceDeploymentManager._perform_health_check")
    
    async def _run_initial_tests(self):
        """Run initial tests to verify services are working."""
        self.logger.info("🧪 Running initial service tests...")
        
        try:
            # Test Scraper Manager
            if 'scraper_manager' in services:
                self.logger.info("🧪 Testing Scraper Manager...")
                scrapers = await services['scraper_manager'].get_scrapers()
                self.logger.info(f"✅ Scraper Manager test passed: {len(scrapers)} scrapers found")
            
            # Test Performance Monitor
            if 'performance_monitor' in services:
                self.logger.info("🧪 Testing Performance Monitor...")
                services['performance_monitor'].start_monitoring()
                await asyncio.sleep(1)
                metrics = services['performance_monitor'].get_system_metrics()
                self.logger.info(f"✅ Performance Monitor test passed: {len(metrics) if metrics else 0} metrics collected")
            
            # Test Coverage Validator
            if 'coverage_validator' in services:
                self.logger.info("🧪 Testing Coverage Validator...")
                coverage_data = services['coverage_validator'].measure_coverage('src')
                self.logger.info(f"✅ Coverage Validator test passed: {coverage_data.get('coverage_percentage', 0):.2f}% coverage")
            
            self.logger.info("✅ All initial tests passed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Initial tests failed: {e}")
            log_error(e, "ServiceDeploymentManager._run_initial_tests")
            raise
    
    async def _start_service_monitoring(self):
        """Start monitoring of all services."""
        self.logger.info("📊 Starting service monitoring...")
        
        try:
            # Start performance monitoring
            if 'performance_monitor' in services:
                services['performance_monitor'].start_monitoring()
                self.logger.info("✅ Performance monitoring started")
            
            # Start ETL monitoring
            asyncio.create_task(self._etl_monitor())
            self.logger.info("✅ ETL monitoring started")
            
            # Start scraper activity monitoring
            asyncio.create_task(self._scraper_activity_monitor())
            self.logger.info("✅ Scraper activity monitoring started")
            
        except Exception as e:
            self.logger.error(f"❌ Service monitoring startup failed: {e}")
            log_error(e, "ServiceDeploymentManager._start_service_monitoring")
    
    async def _etl_monitor(self):
        """Monitor ETL operations."""
        self.logger.info("🔄 ETL monitoring active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Log ETL status
                if 'etl_service' in services:
                    log_etl_operation("status_check", "monitoring", {
                        "timestamp": datetime.utcnow().isoformat(),
                        "service_status": "active"
                    })
                
            except asyncio.CancelledError:
                self.logger.info("🔄 ETL monitoring cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ ETL monitoring error: {e}")
                log_error(e, "ServiceDeploymentManager._etl_monitor")
    
    async def _scraper_activity_monitor(self):
        """Monitor scraper activities."""
        self.logger.info("🕷️ Scraper activity monitoring active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Log scraper status
                if 'scraper_manager' in services:
                    try:
                        status = services['scraper_manager'].get_system_status()
                        log_scraper_activity(0, "status_check", {
                            "active_jobs": status['active_jobs_count'],
                            "health_status": status['health_status'],
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    except Exception as e:
                        self.logger.debug(f"Scraper status check failed: {e}")
                
            except asyncio.CancelledError:
                self.logger.info("🕷️ Scraper activity monitoring cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Scraper activity monitoring error: {e}")
                log_error(e, "ServiceDeploymentManager._scraper_activity_monitor")
    
    async def _run_services(self):
        """Keep services running until shutdown."""
        self.logger.info("🚀 All services are now running and monitoring...")
        self.logger.info("📊 Check logs for detailed information")
        self.logger.info("🛑 Press Ctrl+C to shutdown gracefully")
        
        try:
            # Wait for shutdown signal
            await shutdown_event.wait()
            
        except Exception as e:
            self.logger.error(f"❌ Service runtime error: {e}")
            log_error(e, "ServiceDeploymentManager._run_services")
        finally:
            await self._shutdown_services()
    
    async def _shutdown_services(self):
        """Shutdown all services gracefully."""
        self.logger.info("🛑 Shutting down all services...")
        
        try:
            # Stop performance monitoring
            if 'performance_monitor' in services:
                services['performance_monitor'].stop_monitoring()
                self.logger.info("✅ Performance monitoring stopped")
            
            # Shutdown services in reverse order
            shutdown_order = ['etl_service', 'data_pipeline', 'scraper_manager']
            
            for service_name in shutdown_order:
                if service_name in services:
                    try:
                        service = services[service_name]
                        if hasattr(service, '__aexit__'):
                            await service.__aexit__(None, None, None)
                        self.logger.info(f"✅ {service_name} shutdown completed")
                    except Exception as e:
                        self.logger.error(f"❌ {service_name} shutdown failed: {e}")
                        log_error(e, f"ServiceDeploymentManager._shutdown_services.{service_name}")
            
            # Calculate uptime
            if self.deployment_start_time:
                uptime = (datetime.utcnow() - self.deployment_start_time).total_seconds()
                self.logger.info(f"⏱️ Total service uptime: {uptime:.2f} seconds")
            
            self.logger.info("✅ All services shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Service shutdown failed: {e}")
            log_error(e, "ServiceDeploymentManager._shutdown_services")
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status."""
        return {
            "deployment_start_time": self.deployment_start_time.isoformat() if self.deployment_start_time else None,
            "services_status": self.services_status,
            "total_services": len(self.services_status),
            "deployed_services": len([s for s in self.services_status.values() if s == 'deployed']),
            "uptime": (datetime.utcnow() - self.deployment_start_time).total_seconds() if self.deployment_start_time else 0
        }


async def main():
    """Main deployment function."""
    global startup_time
    startup_time = datetime.utcnow()
    
    print("🚀 OpenPolicy Scraper Service - Comprehensive Deployment")
    print("=" * 60)
    print(f"📅 Deployment started: {startup_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Enhanced logging and monitoring enabled")
    print("📊 All services will be deployed with comprehensive logging")
    print()
    
    try:
        # Create deployment manager
        deployment_manager = ServiceDeploymentManager()
        
        # Deploy all services
        await deployment_manager.deploy_all_services()
        
    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted by user")
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        logging.error(f"Deployment failed: {e}")
        sys.exit(1)
    finally:
        print(f"\n📊 Deployment completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        if startup_time:
            uptime = (datetime.utcnow() - startup_time).total_seconds()
            print(f"⏱️ Total deployment time: {uptime:.2f} seconds")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Deployment stopped by user")
    except Exception as e:
        print(f"\n❌ Deployment error: {e}")
        sys.exit(1)

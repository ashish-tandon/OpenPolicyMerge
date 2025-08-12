#!/usr/bin/env python3
"""
Comprehensive Monitoring and Bug Detection Script for OpenPolicy Scraper Service

This script monitors all services, detects bugs and errors, and provides detailed analysis.
"""

import asyncio
import logging
import sys
import time
import os
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import psutil
import signal

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

# Global variables
monitoring_active = False
shutdown_event = asyncio.Event()
bug_reports = []
error_logs = []
performance_issues = []
startup_time = None

# Signal handlers
def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger = logging.getLogger('monitoring')
    logger.info(f"🛑 Received signal {signum}, stopping monitoring...")
    shutdown_event.set()


class ComprehensiveMonitor:
    """Comprehensive monitoring and bug detection system."""
    
    def __init__(self):
        """Initialize the comprehensive monitor."""
        self.logger = get_logger(__name__)
        self.services = {}
        self.monitoring_start_time = None
        self.check_interval = 15  # 15 seconds
        self.health_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 2.0,  # seconds
            'error_rate': 5.0  # percentage
        }
        
        self.logger.info("🔍 Initializing Comprehensive Monitor")
        self.logger.info(f"🔧 Health thresholds: {self.health_thresholds}")
    
    async def start_monitoring(self):
        """Start comprehensive monitoring."""
        self.logger.info("🚀 Starting comprehensive monitoring...")
        self.monitoring_start_time = datetime.utcnow()
        
        try:
            # Initialize services
            await self._initialize_services()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            # Keep monitoring until shutdown
            await self._run_monitoring()
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring failed: {e}")
            log_error(e, "ComprehensiveMonitor.start_monitoring")
            raise
    
    async def _initialize_services(self):
        """Initialize all services for monitoring."""
        self.logger.info("⚙️ Initializing services for monitoring...")
        
        try:
            # Initialize Scraper Manager
            self.logger.info("🕷️ Initializing Scraper Manager...")
            scraper_manager = ScraperManager()
            await scraper_manager.__aenter__()
            self.services['scraper_manager'] = scraper_manager
            self.logger.info("✅ Scraper Manager initialized")
            
            # Initialize Data Pipeline
            self.logger.info("🔄 Initializing Data Pipeline...")
            data_pipeline = DataPipeline()
            await data_pipeline.__aenter__()
            self.services['data_pipeline'] = data_pipeline
            self.logger.info("✅ Data Pipeline initialized")
            
            # Initialize ETL Service
            self.logger.info("⚙️ Initializing ETL Service...")
            etl_service = ETLService()
            await etl_service.__aenter__()
            self.services['etl_service'] = etl_service
            self.logger.info("✅ ETL Service initialized")
            
            # Initialize Performance Monitor
            self.logger.info("📊 Initializing Performance Monitor...")
            performance_monitor = PerformanceMonitor()
            self.services['performance_monitor'] = performance_monitor
            self.logger.info("✅ Performance Monitor initialized")
            
            # Initialize Coverage Validator
            self.logger.info("📋 Initializing Coverage Validator...")
            coverage_validator = CoverageValidator()
            self.services['coverage_validator'] = coverage_validator
            self.logger.info("✅ Coverage Validator initialized")
            
            self.logger.info(f"✅ All {len(self.services)} services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Service initialization failed: {e}")
            log_error(e, "ComprehensiveMonitor._initialize_services")
            raise
    
    async def _start_monitoring_tasks(self):
        """Start all monitoring tasks."""
        self.logger.info("📊 Starting monitoring tasks...")
        
        try:
            # Start system resource monitoring
            asyncio.create_task(self._monitor_system_resources())
            self.logger.info("✅ System resource monitoring started")
            
            # Start service health monitoring
            asyncio.create_task(self._monitor_service_health())
            self.logger.info("✅ Service health monitoring started")
            
            # Start performance monitoring
            asyncio.create_task(self._monitor_performance())
            self.logger.info("✅ Performance monitoring started")
            
            # Start error detection and analysis
            asyncio.create_task(self._detect_errors_and_bugs())
            self.logger.info("✅ Error detection started")
            
            # Start log analysis
            asyncio.create_task(self._analyze_logs())
            self.logger.info("✅ Log analysis started")
            
            # Start coverage monitoring
            asyncio.create_task(self._monitor_coverage())
            self.logger.info("✅ Coverage monitoring started")
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring tasks startup failed: {e}")
            log_error(e, "ComprehensiveMonitor._start_monitoring_tasks")
    
    async def _monitor_system_resources(self):
        """Monitor system resources continuously."""
        self.logger.info("💻 System resource monitoring active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(self.check_interval)
                await self._check_system_resources()
                
            except asyncio.CancelledError:
                self.logger.info("💻 System resource monitoring cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ System resource monitoring error: {e}")
                log_error(e, "ComprehensiveMonitor._monitor_system_resources")
    
    async def _check_system_resources(self):
        """Check system resources and detect issues."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network stats
            network = psutil.net_io_counters()
            
            # Check thresholds and log issues
            issues = []
            
            if cpu_percent > self.health_thresholds['cpu_usage']:
                issues.append(f"High CPU usage: {cpu_percent}%")
                self._record_performance_issue("high_cpu", cpu_percent, {"threshold": self.health_thresholds['cpu_usage']})
            
            if memory.percent > self.health_thresholds['memory_usage']:
                issues.append(f"High memory usage: {memory.percent}%")
                self._record_performance_issue("high_memory", memory.percent, {"threshold": self.health_thresholds['memory_usage']})
            
            if (disk.used / disk.total) * 100 > self.health_thresholds['disk_usage']:
                issues.append(f"High disk usage: {(disk.used / disk.total) * 100:.1f}%")
                self._record_performance_issue("high_disk", (disk.used / disk.total) * 100, {"threshold": self.health_thresholds['disk_usage']})
            
            # Log system status
            system_status = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "issues": issues
            }
            
            if issues:
                self.logger.warning(f"⚠️ System resource issues detected: {', '.join(issues)}")
                log_system_health("SystemResources", "degraded", system_status)
            else:
                log_system_health("SystemResources", "healthy", system_status)
            
        except Exception as e:
            self.logger.error(f"❌ System resource check failed: {e}")
            log_error(e, "ComprehensiveMonitor._check_system_resources")
    
    async def _monitor_service_health(self):
        """Monitor health of all services."""
        self.logger.info("🏥 Service health monitoring active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(self.check_interval * 2)  # Check every 30 seconds
                await self._check_service_health()
                
            except asyncio.CancelledError:
                self.logger.info("🏥 Service health monitoring cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Service health monitoring error: {e}")
                log_error(e, "ComprehensiveMonitor._monitor_service_health")
    
    async def _check_service_health(self):
        """Check health of all services."""
        try:
            health_results = {}
            
            # Check Scraper Manager
            if 'scraper_manager' in self.services:
                try:
                    status = self.services['scraper_manager'].get_system_status()
                    health_results['scraper_manager'] = {
                        'status': status['health_status'],
                        'active_jobs': status['active_jobs_count'],
                        'uptime': status['uptime']
                    }
                except Exception as e:
                    health_results['scraper_manager'] = {'status': 'error', 'error': str(e)}
                    self._record_error("scraper_manager_health_check", e)
            
            # Check Performance Monitor
            if 'performance_monitor' in self.services:
                try:
                    metrics = self.services['performance_monitor'].get_system_metrics()
                    health_results['performance_monitor'] = {
                        'status': 'healthy',
                        'metrics_count': len(metrics) if metrics else 0
                    }
                except Exception as e:
                    health_results['performance_monitor'] = {'status': 'error', 'error': str(e)}
                    self._record_error("performance_monitor_health_check", e)
            
            # Check Coverage Validator
            if 'coverage_validator' in self.services:
                try:
                    coverage_data = self.services['coverage_validator'].measure_coverage('src')
                    health_results['coverage_validator'] = {
                        'status': 'healthy',
                        'coverage': coverage_data.get('coverage_percentage', 0)
                    }
                except Exception as e:
                    health_results['coverage_validator'] = {'status': 'error', 'error': str(e)}
                    self._record_error("coverage_validator_health_check", e)
            
            # Log overall health
            healthy_services = sum(1 for s in health_results.values() if s.get('status') == 'healthy')
            total_services = len(health_results)
            
            if healthy_services == total_services:
                overall_status = "healthy"
            elif healthy_services > total_services // 2:
                overall_status = "degraded"
            else:
                overall_status = "unhealthy"
            
            log_system_health("AllServices", overall_status, {
                "overall_status": overall_status,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "services": health_results
            })
            
        except Exception as e:
            self.logger.error(f"❌ Service health check failed: {e}")
            log_error(e, "ComprehensiveMonitor._check_service_health")
    
    async def _monitor_performance(self):
        """Monitor performance metrics."""
        self.logger.info("⚡ Performance monitoring active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(self.check_interval * 4)  # Check every minute
                await self._check_performance()
                
            except asyncio.CancelledError:
                self.logger.info("⚡ Performance monitoring cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Performance monitoring error: {e}")
                log_error(e, "ComprehensiveMonitor._monitor_performance")
    
    async def _check_performance(self):
        """Check performance metrics."""
        try:
            if 'performance_monitor' in self.services:
                # Start monitoring temporarily
                self.services['performance_monitor'].start_monitoring()
                await asyncio.sleep(2)
                
                # Get metrics
                metrics = self.services['performance_monitor'].get_system_metrics()
                
                if metrics:
                    # Analyze performance
                    for metric_name, metric_data in metrics.items():
                        if isinstance(metric_data, (int, float)):
                            # Check for performance anomalies
                            if metric_data > 1000:  # Example threshold
                                self._record_performance_issue("high_metric", metric_data, {
                                    "metric_name": metric_name,
                                    "threshold": 1000
                                })
                
                # Stop monitoring
                self.services['performance_monitor'].stop_monitoring()
                
        except Exception as e:
            self.logger.error(f"❌ Performance check failed: {e}")
            log_error(e, "ComprehensiveMonitor._check_performance")
    
    async def _detect_errors_and_bugs(self):
        """Detect and analyze errors and bugs."""
        self.logger.info("🐛 Error detection and bug analysis active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(self.check_interval * 3)  # Check every 45 seconds
                await self._analyze_errors_and_bugs()
                
            except asyncio.CancelledError:
                self.logger.info("🐛 Error detection cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Error detection failed: {e}")
                log_error(e, "ComprehensiveMonitor._detect_errors_and_bugs")
    
    async def _analyze_errors_and_bugs(self):
        """Analyze errors and bugs."""
        try:
            # Check for recent errors in logs
            await self._check_error_logs()
            
            # Check for service exceptions
            await self._check_service_exceptions()
            
            # Check for data inconsistencies
            await self._check_data_inconsistencies()
            
        except Exception as e:
            self.logger.error(f"❌ Error and bug analysis failed: {e}")
            log_error(e, "ComprehensiveMonitor._analyze_errors_and_bugs")
    
    async def _check_error_logs(self):
        """Check error logs for issues."""
        try:
            # Check if error log file exists and has recent entries
            error_log_file = Path("logs/errors.log")
            if error_log_file.exists():
                # Read recent error log entries
                with open(error_log_file, 'r') as f:
                    lines = f.readlines()
                    recent_errors = lines[-50:] if len(lines) > 50 else lines
                
                # Analyze error patterns
                error_patterns = {}
                for line in recent_errors:
                    if 'ERROR' in line:
                        # Extract error type and message
                        if 'ImportError' in line:
                            error_patterns['ImportError'] = error_patterns.get('ImportError', 0) + 1
                        elif 'AttributeError' in line:
                            error_patterns['AttributeError'] = error_patterns.get('AttributeError', 0) + 1
                        elif 'ConnectionError' in line:
                            error_patterns['ConnectionError'] = error_patterns.get('ConnectionError', 0) + 1
                        elif 'TimeoutError' in line:
                            error_patterns['TimeoutError'] = error_patterns.get('TimeoutError', 0) + 1
                
                # Report error patterns
                for error_type, count in error_patterns.items():
                    if count > 3:  # Threshold for reporting
                        self._record_bug("frequent_errors", {
                            "error_type": error_type,
                            "count": count,
                            "threshold": 3,
                            "log_file": "errors.log"
                        })
            
        except Exception as e:
            self.logger.error(f"❌ Error log check failed: {e}")
            log_error(e, "ComprehensiveMonitor._check_error_logs")
    
    async def _check_service_exceptions(self):
        """Check for service exceptions."""
        try:
            # Test service operations to detect runtime errors
            if 'scraper_manager' in self.services:
                try:
                    # Test basic operation
                    scrapers = await self.services['scraper_manager'].get_scrapers()
                    if not scrapers:
                        self._record_bug("no_scrapers_found", {
                            "service": "scraper_manager",
                            "operation": "get_scrapers",
                            "expected": "list of scrapers",
                            "actual": "empty list"
                        })
                except Exception as e:
                    self._record_error("scraper_manager_operation", e)
            
            if 'coverage_validator' in self.services:
                try:
                    # Test coverage measurement
                    coverage_data = self.services['coverage_validator'].measure_coverage('src')
                    if not coverage_data or coverage_data.get('coverage_percentage', 0) == 0:
                        self._record_bug("coverage_measurement_failed", {
                            "service": "coverage_validator",
                            "operation": "measure_coverage",
                            "expected": "coverage data",
                            "actual": coverage_data
                        })
                except Exception as e:
                    self._record_error("coverage_validator_operation", e)
                    
        except Exception as e:
            self.logger.error(f"❌ Service exception check failed: {e}")
            log_error(e, "ComprehensiveMonitor._check_service_exceptions")
    
    async def _check_data_inconsistencies(self):
        """Check for data inconsistencies."""
        try:
            # Check for data consistency issues
            if 'scraper_manager' in self.services:
                try:
                    status = self.services['scraper_manager'].get_system_status()
                    
                    # Check for inconsistencies
                    if status.get('active_jobs_count', 0) < 0:
                        self._record_bug("negative_job_count", {
                            "service": "scraper_manager",
                            "field": "active_jobs_count",
                            "value": status.get('active_jobs_count'),
                            "expected": "non-negative integer"
                        })
                    
                    if status.get('uptime', 0) < 0:
                        self._record_bug("negative_uptime", {
                            "service": "scraper_manager",
                            "field": "uptime",
                            "value": status.get('uptime'),
                            "expected": "non-negative number"
                        })
                        
                except Exception as e:
                    self._record_error("data_consistency_check", e)
                    
        except Exception as e:
            self.logger.error(f"❌ Data consistency check failed: {e}")
            log_error(e, "ComprehensiveMonitor._check_data_inconsistencies")
    
    async def _analyze_logs(self):
        """Analyze log files for patterns and issues."""
        self.logger.info("📋 Log analysis active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(self.check_interval * 6)  # Check every 90 seconds
                await self._perform_log_analysis()
                
            except asyncio.CancelledError:
                self.logger.info("📋 Log analysis cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Log analysis failed: {e}")
                log_error(e, "ComprehensiveMonitor._analyze_log_analysis")
    
    async def _perform_log_analysis(self):
        """Perform comprehensive log analysis."""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return
            
            # Analyze different log files
            for log_file in logs_dir.glob("*.log"):
                await self._analyze_single_log(log_file)
                
        except Exception as e:
            self.logger.error(f"❌ Log analysis failed: {e}")
            log_error(e, "ComprehensiveMonitor._perform_log_analysis")
    
    async def _analyze_single_log(self, log_file: Path):
        """Analyze a single log file."""
        try:
            if not log_file.exists():
                return
            
            # Read recent log entries
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            # Analyze patterns
            patterns = {
                'errors': 0,
                'warnings': 0,
                'critical': 0,
                'exceptions': 0
            }
            
            for line in recent_lines:
                if 'ERROR' in line:
                    patterns['errors'] += 1
                elif 'WARNING' in line:
                    patterns['warnings'] += 1
                elif 'CRITICAL' in line:
                    patterns['critical'] += 1
                elif 'Exception' in line or 'Traceback' in line:
                    patterns['exceptions'] += 1
            
            # Report concerning patterns
            if patterns['errors'] > 10:
                self._record_bug("high_error_rate", {
                    "log_file": log_file.name,
                    "error_count": patterns['errors'],
                    "threshold": 10,
                    "analysis_period": "100 lines"
                })
            
            if patterns['exceptions'] > 5:
                self._record_bug("frequent_exceptions", {
                    "log_file": log_file.name,
                    "exception_count": patterns['exceptions'],
                    "threshold": 5,
                    "analysis_period": "100 lines"
                })
                
        except Exception as e:
            self.logger.error(f"❌ Single log analysis failed for {log_file}: {e}")
            log_error(e, "ComprehensiveMonitor._analyze_single_log")
    
    async def _monitor_coverage(self):
        """Monitor code coverage."""
        self.logger.info("📊 Coverage monitoring active")
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(self.check_interval * 8)  # Check every 2 minutes
                await self._check_coverage()
                
            except asyncio.CancelledError:
                self.logger.info("📊 Coverage monitoring cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Coverage monitoring failed: {e}")
                log_error(e, "ComprehensiveMonitor._monitor_coverage")
    
    async def _check_coverage(self):
        """Check code coverage."""
        try:
            if 'coverage_validator' in self.services:
                coverage_data = self.services['coverage_validator'].measure_coverage('src')
                
                if coverage_data:
                    coverage_percentage = coverage_data.get('coverage_percentage', 0)
                    
                    # Check if coverage is below threshold
                    if coverage_percentage < 80.0:
                        self._record_bug("low_coverage", {
                            "current_coverage": coverage_percentage,
                            "threshold": 80.0,
                            "gap": 80.0 - coverage_percentage,
                            "modules_count": coverage_data.get('modules_count', 0)
                        })
                    
                    # Check for coverage gaps
                    gaps = self.services['coverage_validator'].identify_coverage_gaps()
                    if gaps:
                        self._record_bug("coverage_gaps", {
                            "gaps_count": len(gaps),
                            "gaps": gaps[:5]  # First 5 gaps
                        })
                        
        except Exception as e:
            self.logger.error(f"❌ Coverage check failed: {e}")
            log_error(e, "ComprehensiveMonitor._check_coverage")
    
    def _record_error(self, context: str, error: Exception):
        """Record an error for analysis."""
        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        
        error_logs.append(error_record)
        self.logger.error(f"🚨 Error recorded: {context} - {type(error).__name__}: {str(error)}")
    
    def _record_bug(self, bug_type: str, details: Dict[str, Any]):
        """Record a bug for analysis."""
        bug_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "bug_type": bug_type,
            "details": details,
            "severity": self._assess_bug_severity(bug_type, details)
        }
        
        bug_reports.append(bug_report)
        self.logger.warning(f"🐛 Bug detected: {bug_type} - {details}")
    
    def _record_performance_issue(self, issue_type: str, value: float, context: Dict[str, Any]):
        """Record a performance issue."""
        performance_issue = {
            "timestamp": datetime.utcnow().isoformat(),
            "issue_type": issue_type,
            "value": value,
            "context": context,
            "severity": self._assess_performance_severity(issue_type, value)
        }
        
        performance_issues.append(performance_issue)
        self.logger.warning(f"⚡ Performance issue: {issue_type} - {value}")
    
    def _assess_bug_severity(self, bug_type: str, details: Dict[str, Any]) -> str:
        """Assess the severity of a bug."""
        critical_bugs = ['frequent_exceptions', 'high_error_rate', 'data_corruption']
        high_bugs = ['low_coverage', 'service_failure', 'data_inconsistency']
        
        if bug_type in critical_bugs:
            return "critical"
        elif bug_type in high_bugs:
            return "high"
        else:
            return "medium"
    
    def _assess_performance_severity(self, issue_type: str, value: float) -> str:
        """Assess the severity of a performance issue."""
        if value > 95:
            return "critical"
        elif value > 85:
            return "high"
        else:
            return "medium"
    
    async def _run_monitoring(self):
        """Run monitoring until shutdown."""
        self.logger.info("🔍 Comprehensive monitoring is now active...")
        self.logger.info("📊 Monitoring all services, resources, and detecting issues...")
        self.logger.info("🛑 Press Ctrl+C to stop monitoring")
        
        try:
            # Wait for shutdown signal
            await shutdown_event.wait()
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring runtime error: {e}")
            log_error(e, "ComprehensiveMonitor._run_monitoring")
        finally:
            await self._shutdown_monitoring()
    
    async def _shutdown_monitoring(self):
        """Shutdown monitoring gracefully."""
        self.logger.info("🛑 Shutting down monitoring...")
        
        try:
            # Shutdown services
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, '__aexit__'):
                        await service.__aexit__(None, None, None)
                    self.logger.info(f"✅ {service_name} shutdown completed")
                except Exception as e:
                    self.logger.error(f"❌ {service_name} shutdown failed: {e}")
            
            # Generate final report
            await self._generate_final_report()
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring shutdown failed: {e}")
            log_error(e, "ComprehensiveMonitor._shutdown_monitoring")
    
    async def _generate_final_report(self):
        """Generate final monitoring and bug report."""
        self.logger.info("📋 Generating final monitoring report...")
        
        try:
            # Calculate monitoring duration
            if self.monitoring_start_time:
                duration = (datetime.utcnow() - self.monitoring_start_time).total_seconds()
            else:
                duration = 0
            
            # Generate comprehensive report
            report = {
                "monitoring_session": {
                    "start_time": self.monitoring_start_time.isoformat() if self.monitoring_start_time else None,
                    "end_time": datetime.utcnow().isoformat(),
                    "duration_seconds": duration,
                    "check_interval": self.check_interval
                },
                "issues_detected": {
                    "total_bugs": len(bug_reports),
                    "total_errors": len(error_logs),
                    "total_performance_issues": len(performance_issues)
                },
                "bug_reports": bug_reports,
                "error_logs": error_logs[-20:],  # Last 20 errors
                "performance_issues": performance_issues,
                "recommendations": self._generate_recommendations()
            }
            
            # Save report to file
            report_file = f"comprehensive_monitoring_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"📋 Final report saved to: {report_file}")
            
            # Print summary
            print("\n" + "=" * 80)
            print("🔍 COMPREHENSIVE MONITORING REPORT")
            print("=" * 80)
            print(f"📅 Monitoring Duration: {duration:.2f} seconds")
            print(f"🐛 Bugs Detected: {len(bug_reports)}")
            print(f"🚨 Errors Logged: {len(error_logs)}")
            print(f"⚡ Performance Issues: {len(performance_issues)}")
            print(f"📋 Detailed Report: {report_file}")
            print("=" * 80)
            
        except Exception as e:
            self.logger.error(f"❌ Final report generation failed: {e}")
            log_error(e, "ComprehensiveMonitor._generate_final_report")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on detected issues."""
        recommendations = []
        
        # Analyze bug patterns
        bug_types = [bug['bug_type'] for bug in bug_reports]
        
        if 'frequent_exceptions' in bug_types:
            recommendations.append("Review error handling and add more robust exception management")
        
        if 'high_error_rate' in bug_types:
            recommendations.append("Investigate root causes of frequent errors and implement fixes")
        
        if 'low_coverage' in bug_types:
            recommendations.append("Increase test coverage by adding more unit and integration tests")
        
        if 'data_inconsistency' in bug_types:
            recommendations.append("Review data validation and consistency checks")
        
        if 'performance_issues' in [issue['issue_type'] for issue in performance_issues]:
            recommendations.append("Optimize performance bottlenecks and resource usage")
        
        if not recommendations:
            recommendations.append("System appears to be running well with no major issues detected")
        
        return recommendations


async def main():
    """Main monitoring function."""
    global startup_time
    startup_time = datetime.utcnow()
    
    print("🔍 OpenPolicy Scraper Service - Comprehensive Monitoring & Bug Detection")
    print("=" * 80)
    print(f"📅 Monitoring started: {startup_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Enhanced logging and comprehensive monitoring enabled")
    print("🐛 Bug detection and error analysis active")
    print("📊 Performance monitoring and health checks running")
    print()
    
    try:
        # Create comprehensive monitor
        monitor = ComprehensiveMonitor()
        
        # Start monitoring
        await monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring failed: {e}")
        logging.error(f"Monitoring failed: {e}")
        sys.exit(1)
    finally:
        print(f"\n📊 Monitoring completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        if startup_time:
            uptime = (datetime.utcnow() - startup_time).total_seconds()
            print(f"⏱️ Total monitoring time: {uptime:.2f} seconds")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
System Status Report for OpenPolicy Scraper Service

This script provides a comprehensive overview of the system status.
"""

import psycopg2
import logging
from datetime import datetime
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.coverage_validator import CoverageValidator

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


def check_database_health():
    """Check database health and status."""
    logger.info("🔍 Checking Database Health...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check table counts
        tables = ['scraper_info', 'scraper_jobs', 'scraper_logs', 'data_collection', 'analytics_summary']
        table_counts = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_counts[table] = count
            except Exception as e:
                logger.warning(f"Error counting {table}: {e}")
                table_counts[table] = 0
        
        # Check scraper statuses
        cursor.execute("SELECT status, COUNT(*) FROM scraper_info GROUP BY status")
        scraper_statuses = dict(cursor.fetchall())
        
        # Check recent job activity
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM scraper_jobs 
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY status
        """)
        recent_jobs = dict(cursor.fetchall())
        
        cursor.close()
        conn.close()
        
        return {
            "table_counts": table_counts,
            "scraper_statuses": scraper_statuses,
            "recent_jobs": recent_jobs,
            "database_healthy": True
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"database_healthy": False, "error": str(e)}


def check_system_resources():
    """Check system resource usage."""
    logger.info("💻 Checking System Resources...")
    
    try:
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Network stats
        network = psutil.net_io_counters()
        
        return {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        }
        
    except ImportError:
        logger.warning("psutil not available, skipping system resource check")
        return {"error": "psutil not available"}
    except Exception as e:
        logger.error(f"System resource check failed: {e}")
        return {"error": str(e)}


def check_coverage_status():
    """Check code coverage status."""
    logger.info("📊 Checking Code Coverage...")
    
    try:
        validator = CoverageValidator(85.0)
        coverage_data = validator.measure_coverage('src')
        
        return {
            "coverage_percentage": coverage_data.get("coverage_percentage", 0.0),
            "total_lines": coverage_data.get("total_lines", 0),
            "covered_lines": coverage_data.get("covered_lines", 0),
            "meets_threshold": validator.validate_threshold(),
            "threshold": validator.coverage_threshold,
            "modules_count": len(coverage_data.get("modules", {}))
        }
        
    except Exception as e:
        logger.error(f"Coverage check failed: {e}")
        return {"error": str(e)}


def check_service_status():
    """Check service status and health."""
    logger.info("⚙️ Checking Service Status...")
    
    try:
        # Check if key services can be imported
        services_status = {}
        
        try:
            from src.services.scraper_manager import ScraperManager
            services_status["scraper_manager"] = "available"
        except Exception as e:
            services_status["scraper_manager"] = f"error: {e}"
        
        try:
            from src.services.data_pipeline import DataPipeline
            services_status["data_pipeline"] = "available"
        except Exception as e:
            services_status["data_pipeline"] = f"error: {e}"
        
        try:
            from src.services.etl_service import ETLService
            services_status["etl_service"] = "available"
        except Exception as e:
            services_status["etl_service"] = f"error: {e}"
        
        try:
            from src.services.performance_monitor import PerformanceMonitor
            services_status["performance_monitor"] = "available"
        except Exception as e:
            services_status["performance_monitor"] = f"error: {e}"
        
        try:
            from src.services.coverage_validator import CoverageValidator
            services_status["coverage_validator"] = "available"
        except Exception as e:
            services_status["coverage_validator"] = f"error: {e}"
        
        return services_status
        
    except Exception as e:
        logger.error(f"Service status check failed: {e}")
        return {"error": str(e)}


def generate_system_report():
    """Generate comprehensive system report."""
    logger.info("📋 Generating System Status Report...")
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": "OpenPolicy Scraper Service",
        "version": "1.0.0",
        "database_health": check_database_health(),
        "system_resources": check_system_resources(),
        "coverage_status": check_coverage_status(),
        "service_status": check_service_status()
    }
    
    return report


def print_report(report):
    """Print the system report in a readable format."""
    print("\n" + "=" * 80)
    print("🚀 OPENPOLICY SCRAPER SERVICE - SYSTEM STATUS REPORT")
    print("=" * 80)
    print(f"📅 Generated: {report['timestamp']}")
    print(f"🏷️  Version: {report['version']}")
    print()
    
    # Database Health
    print("🗄️  DATABASE HEALTH")
    print("-" * 40)
    db_health = report['database_health']
    if db_health.get('database_healthy'):
        print("✅ Database: HEALTHY")
        print(f"   Tables: {len(db_health['table_counts'])}")
        for table, count in db_health['table_counts'].items():
            print(f"   - {table}: {count} records")
        
        print(f"   Scraper Statuses: {db_health['scraper_statuses']}")
        print(f"   Recent Jobs (24h): {db_health['recent_jobs']}")
    else:
        print("❌ Database: UNHEALTHY")
        print(f"   Error: {db_health.get('error', 'Unknown error')}")
    print()
    
    # System Resources
    print("💻 SYSTEM RESOURCES")
    print("-" * 40)
    sys_resources = report['system_resources']
    if 'error' not in sys_resources:
        print(f"   CPU Usage: {sys_resources['cpu_percent']:.1f}%")
        print(f"   Memory Usage: {sys_resources['memory']['percent']:.1f}%")
        print(f"   Disk Usage: {sys_resources['disk']['percent']:.1f}%")
        print(f"   Network Sent: {sys_resources['network']['bytes_sent']:,} bytes")
        print(f"   Network Received: {sys_resources['network']['bytes_recv']:,} bytes")
    else:
        print(f"   Error: {sys_resources['error']}")
    print()
    
    # Coverage Status
    print("📊 CODE COVERAGE")
    print("-" * 40)
    coverage = report['coverage_status']
    if 'error' not in coverage:
        print(f"   Coverage: {coverage['coverage_percentage']:.2f}%")
        print(f"   Threshold: {coverage['threshold']}%")
        print(f"   Status: {'✅ PASS' if coverage['meets_threshold'] else '❌ FAIL'}")
        print(f"   Total Lines: {coverage['total_lines']:,}")
        print(f"   Covered Lines: {coverage['covered_lines']:,}")
        print(f"   Modules: {coverage['modules_count']}")
    else:
        print(f"   Error: {coverage['error']}")
    print()
    
    # Service Status
    print("⚙️  SERVICE STATUS")
    print("-" * 40)
    services = report['service_status']
    for service, status in services.items():
        if status == "available":
            print(f"   {service}: ✅ AVAILABLE")
        else:
            print(f"   {service}: ❌ {status}")
    print()
    
    # Overall Health
    print("🏥 OVERALL SYSTEM HEALTH")
    print("-" * 40)
    
    db_healthy = db_health.get('database_healthy', False)
    coverage_healthy = coverage.get('meets_threshold', False) if 'error' not in coverage else False
    services_healthy = all(status == "available" for status in services.values())
    
    if db_healthy and coverage_healthy and services_healthy:
        print("🎉 SYSTEM STATUS: EXCELLENT")
        print("   All components are healthy and operational")
    elif db_healthy and services_healthy:
        print("⚠️  SYSTEM STATUS: GOOD")
        print("   Core services operational, coverage needs improvement")
    elif db_healthy:
        print("⚠️  SYSTEM STATUS: FAIR")
        print("   Database healthy, some services have issues")
    else:
        print("❌ SYSTEM STATUS: POOR")
        print("   Critical issues detected")
    
    print("\n" + "=" * 80)


def main():
    """Main function to generate and display system report."""
    logger.info("🚀 Starting System Status Report Generation")
    
    try:
        # Generate report
        report = generate_system_report()
        
        # Print report
        print_report(report)
        
        # Save report to file
        report_file = f"system_status_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"System report saved to: {report_file}")
        
        # Return exit code based on system health
        db_healthy = report['database_health'].get('database_healthy', False)
        coverage_healthy = report['coverage_status'].get('meets_threshold', False) if 'error' not in report['coverage_status'] else False
        
        if db_healthy and coverage_healthy:
            logger.info("✅ System is healthy")
            return 0
        else:
            logger.warning("⚠️  System has issues")
            return 1
            
    except Exception as e:
        logger.error(f"System report generation failed: {e}")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

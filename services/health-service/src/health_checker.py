import logging
import asyncio
import httpx
import psutil
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from .database import get_session
import json
import uuid

logger = logging.getLogger(__name__)

class HealthChecker:
    """Comprehensive health checking for OpenPolicy platform"""
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.health_cache = {}
        self.cache_ttl = 60  # 1 minute
        self.last_cache_update = None
        
        # Service endpoints to check
        self.service_endpoints = {
            "policy-service": "http://policy-service:8000/healthz",
            "search-service": "http://search-service:8000/healthz",
            "auth-service": "http://auth-service:8000/healthz",
            "notification-service": "http://notification-service:8000/healthz",
            "config-service": "http://config-service:8000/healthz",
            "monitoring-service": "http://monitoring-service:8000/healthz",
            "etl-service": "http://etl-service:8000/healthz",
            "scraper-service": "http://scraper-service:8000/healthz",
            "health-service": "http://health-service:8000/healthz",
            "plotly-service": "http://plotly-service:8000/healthz",
            "legacy-django": "http://legacy-django:8000/health/",
            "mcp-service": "http://mcp-service:8000/healthz"
        }
    
    async def check_overall_health(self) -> Dict[str, Any]:
        """
        Check overall platform health
        
        Returns:
            Overall health status
        """
        try:
            start_time = time.time()
            
            # Check all services concurrently
            service_health_tasks = []
            for service_name, endpoint in self.service_endpoints.items():
                task = self.check_service_health(service_name, endpoint)
                service_health_tasks.append(task)
            
            # Execute all health checks
            service_results = await asyncio.gather(*service_health_tasks, return_exceptions=True)
            
            # Process results
            service_health = {}
            healthy_services = 0
            total_services = len(self.service_endpoints)
            
            for i, (service_name, _) in enumerate(self.service_endpoints.items()):
                if isinstance(service_results[i], Exception):
                    service_health[service_name] = {
                        "status": "unhealthy",
                        "error": str(service_results[i]),
                        "response_time": None,
                        "last_check": datetime.now().isoformat()
                    }
                else:
                    service_health[service_name] = service_results[i]
                    if service_results[i]["status"] == "healthy":
                        healthy_services += 1
            
            # Check system resources
            system_health = await self.check_system_health()
            
            # Check database health
            database_health = await self.check_database_health()
            
            # Calculate overall status
            overall_status = "healthy" if healthy_services == total_services else "degraded"
            if healthy_services == 0:
                overall_status = "unhealthy"
            
            # Calculate health score (0-100)
            health_score = int((healthy_services / total_services) * 100)
            
            total_time = time.time() - start_time
            
            overall_health = {
                "status": overall_status,
                "health_score": health_score,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "services": service_health,
                "system": system_health,
                "database": database_health,
                "last_check": datetime.now().isoformat(),
                "check_duration": round(total_time, 3)
            }
            
            # Cache the result
            self.health_cache["overall"] = overall_health
            self.last_cache_update = datetime.now()
            
            return overall_health
            
        except Exception as e:
            logger.error(f"Overall health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def check_service_health(self, service_name: str, endpoint: str) -> Dict[str, Any]:
        """
        Check health of a specific service
        
        Args:
            service_name: Name of the service
            endpoint: Health check endpoint
        
        Returns:
            Service health status
        """
        try:
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        health_data = response.json()
                        status = health_data.get("status", "unknown")
                        
                        # Determine if service is healthy
                        if status in ["ok", "healthy", "ready"]:
                            health_status = "healthy"
                        elif status in ["degraded", "warning"]:
                            health_status = "degraded"
                        else:
                            health_status = "unhealthy"
                        
                        return {
                            "status": health_status,
                            "response_time": round(response_time, 3),
                            "status_code": response.status_code,
                            "details": health_data,
                            "last_check": datetime.now().isoformat()
                        }
                        
                    except json.JSONDecodeError:
                        return {
                            "status": "unhealthy",
                            "response_time": round(response_time, 3),
                            "status_code": response.status_code,
                            "error": "Invalid JSON response",
                            "last_check": datetime.now().isoformat()
                        }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time": round(response_time, 3),
                        "status_code": response.status_code,
                        "error": f"HTTP {response.status_code}",
                        "last_check": datetime.now().isoformat()
                    }
                    
        except httpx.TimeoutException:
            return {
                "status": "unhealthy",
                "response_time": None,
                "error": "Timeout",
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time": None,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """
        Check system resource health
        
        Returns:
            System health status
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Determine system health
            system_status = "healthy"
            warnings = []
            
            if cpu_percent > 80:
                system_status = "degraded"
                warnings.append(f"High CPU usage: {cpu_percent}%")
            
            if memory_percent > 85:
                system_status = "degraded"
                warnings.append(f"High memory usage: {memory_percent}%")
            
            if disk_percent > 90:
                system_status = "degraded"
                warnings.append(f"High disk usage: {disk_percent}%")
            
            if cpu_percent > 95 or memory_percent > 95 or disk_percent > 95:
                system_status = "unhealthy"
            
            return {
                "status": system_status,
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory_available,
                    "used": memory.used,
                    "percent": memory_percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk_free,
                    "percent": disk_percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "warnings": warnings,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """
        Check database health
        
        Returns:
            Database health status
        """
        try:
            start_time = time.time()
            
            session = get_session()
            
            # Test basic connectivity
            result = session.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()
            
            if not test_value or test_value[0] != 1:
                return {
                    "status": "unhealthy",
                    "error": "Database connectivity test failed",
                    "response_time": None,
                    "last_check": datetime.now().isoformat()
                }
            
            # Check database size
            size_result = session.execute(text("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as size,
                    pg_database_size(current_database()) as size_bytes
            """))
            db_size = size_result.fetchone()
            
            # Check active connections
            connections_result = session.execute(text("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity 
                WHERE state = 'active'
            """))
            active_connections = connections_result.fetchone()
            
            # Check slow queries
            slow_queries_result = session.execute(text("""
                SELECT count(*) as slow_queries
                FROM pg_stat_activity 
                WHERE state = 'active' 
                AND now() - query_start > interval '5 seconds'
            """))
            slow_queries = slow_queries_result.fetchone()
            
            response_time = time.time() - start_time
            
            # Determine database health
            db_status = "healthy"
            warnings = []
            
            if slow_queries[0] > 10:
                db_status = "degraded"
                warnings.append(f"High number of slow queries: {slow_queries[0]}")
            
            if active_connections[0] > 80:
                db_status = "degraded"
                warnings.append(f"High number of active connections: {active_connections[0]}")
            
            return {
                "status": db_status,
                "response_time": round(response_time, 3),
                "size": db_size[0] if db_size else "Unknown",
                "size_bytes": db_size[1] if db_size else 0,
                "active_connections": active_connections[0] if active_connections else 0,
                "slow_queries": slow_queries[0] if slow_queries else 0,
                "warnings": warnings,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def check_service_dependencies(self, service_name: str) -> Dict[str, Any]:
        """
        Check dependencies for a specific service
        
        Args:
            service_name: Name of the service
        
        Returns:
            Dependency health status
        """
        try:
            # Define service dependencies
            dependencies = {
                "policy-service": ["database", "opa-service", "auth-service"],
                "search-service": ["database", "auth-service"],
                "auth-service": ["database", "config-service"],
                "notification-service": ["database", "redis", "auth-service"],
                "config-service": ["database"],
                "monitoring-service": ["database", "prometheus"],
                "etl-service": ["database", "redis", "celery"],
                "scraper-service": ["database", "redis", "celery"]
            }
            
            service_deps = dependencies.get(service_name, [])
            
            if not service_deps:
                return {
                    "status": "healthy",
                    "dependencies": [],
                    "message": "No dependencies defined"
                }
            
            # Check each dependency
            dep_health = {}
            healthy_deps = 0
            
            for dep in service_deps:
                if dep == "database":
                    dep_status = await self.check_database_health()
                elif dep == "redis":
                    dep_status = await self.check_redis_health()
                elif dep == "celery":
                    dep_status = await self.check_celery_health()
                elif dep == "prometheus":
                    dep_status = await self.check_prometheus_health()
                else:
                    # Check other services
                    dep_endpoint = self.service_endpoints.get(dep)
                    if dep_endpoint:
                        dep_status = await self.check_service_health(dep, dep_endpoint)
                    else:
                        dep_status = {"status": "unknown", "error": "Service not found"}
                
                dep_health[dep] = dep_status
                if dep_status.get("status") == "healthy":
                    healthy_deps += 1
            
            # Calculate dependency health score
            total_deps = len(service_deps)
            dep_health_score = int((healthy_deps / total_deps) * 100) if total_deps > 0 else 100
            
            # Determine overall dependency status
            if healthy_deps == total_deps:
                dep_status = "healthy"
            elif healthy_deps > 0:
                dep_status = "degraded"
            else:
                dep_status = "unhealthy"
            
            return {
                "status": dep_status,
                "health_score": dep_health_score,
                "healthy_dependencies": healthy_deps,
                "total_dependencies": total_deps,
                "dependencies": dep_health,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dependency health check failed for {service_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            # This would check Redis connectivity
            # For now, return a placeholder
            return {
                "status": "healthy",
                "message": "Redis health check not implemented",
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def check_celery_health(self) -> Dict[str, Any]:
        """Check Celery health"""
        try:
            # This would check Celery worker status
            # For now, return a placeholder
            return {
                "status": "healthy",
                "message": "Celery health check not implemented",
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def check_prometheus_health(self) -> Dict[str, Any]:
        """Check Prometheus health"""
        try:
            # This would check Prometheus endpoint
            # For now, return a placeholder
            return {
                "status": "healthy",
                "message": "Prometheus health check not implemented",
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def get_health_history(self, service_name: str = None, 
                                hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get health check history
        
        Args:
            service_name: Specific service name (optional)
            hours: Number of hours to look back
        
        Returns:
            Health check history
        """
        try:
            session = get_session()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = """
                SELECT service_name, status, health_score, details, created_at
                FROM monitoring.health_checks 
                WHERE created_at >= :cutoff_time
            """
            params = {"cutoff_time": cutoff_time}
            
            if service_name:
                query += " AND service_name = :service_name"
                params["service_name"] = service_name
            
            query += " ORDER BY created_at DESC"
            
            result = session.execute(text(query), params).fetchall()
            
            history = []
            for row in result:
                history_entry = dict(row)
                history_entry["created_at"] = history_entry["created_at"].isoformat() if history_entry["created_at"] else None
                
                # Parse details JSON
                if history_entry.get("details"):
                    try:
                        history_entry["details"] = json.loads(history_entry["details"])
                    except json.JSONDecodeError:
                        pass
                
                history.append(history_entry)
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get health history: {e}")
            return []
    
    async def store_health_check(self, service_name: str, status: str, 
                                health_score: int = None, details: Dict = None):
        """
        Store health check result in database
        
        Args:
            service_name: Name of the service
            status: Health status
            health_score: Health score (0-100)
            details: Additional health details
        """
        try:
            session = get_session()
            
            session.execute(
                text("""
                    INSERT INTO monitoring.health_checks 
                    (id, service_name, status, health_score, details, created_at)
                    VALUES (:id, :service_name, :status, :health_score, :details, NOW())
                """),
                {
                    "id": str(uuid.uuid4()),
                    "service_name": service_name,
                    "status": status,
                    "health_score": health_score,
                    "details": json.dumps(details) if details else None
                }
            )
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Failed to store health check: {e}")
    
    def is_cache_valid(self) -> bool:
        """Check if health cache is still valid"""
        if not self.last_cache_update:
            return False
        
        return (datetime.now() - self.last_cache_update).total_seconds() < self.cache_ttl
    
    def get_cached_health(self, key: str = "overall") -> Optional[Dict[str, Any]]:
        """Get cached health data"""
        if self.is_cache_valid():
            return self.health_cache.get(key)
        return None
    
    async def start_periodic_health_checks(self, interval: int = 60):
        """
        Start periodic health checking
        
        Args:
            interval: Check interval in seconds
        """
        while True:
            try:
                logger.info("Starting periodic health checks...")
                
                # Perform overall health check
                overall_health = await self.check_overall_health()
                
                # Store results
                await self.store_health_check(
                    "overall",
                    overall_health["status"],
                    overall_health.get("health_score"),
                    overall_health
                )
                
                # Store individual service results
                for service_name, service_health in overall_health.get("services", {}).items():
                    await self.store_health_check(
                        service_name,
                        service_health["status"],
                        None,  # Individual services don't have health scores
                        service_health
                    )
                
                logger.info(f"Periodic health check completed. Status: {overall_health['status']}")
                
                # Wait for next check
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Periodic health check failed: {e}")
                await asyncio.sleep(interval)

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import json
import time

from src.health_checker import HealthChecker

@pytest.fixture
def health_checker():
    """Create health checker instance"""
    return HealthChecker()

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = Mock()
    session.execute = Mock()
    session.commit = Mock()
    return session

@pytest.fixture
def sample_service_health():
    """Sample service health data"""
    return {
        "status": "healthy",
        "response_time": 0.05,
        "status_code": 200,
        "details": {"status": "ok"},
        "last_check": datetime.now().isoformat()
    }

class TestHealthChecker:
    """Test cases for HealthChecker"""
    
    def test_initialization(self, health_checker):
        """Test HealthChecker initialization"""
        assert health_checker.timeout == 10.0
        assert health_checker.health_cache == {}
        assert health_checker.cache_ttl == 60
        assert health_checker.last_cache_update is None
        assert len(health_checker.service_endpoints) > 0
        assert "policy-service" in health_checker.service_endpoints
        assert "search-service" in health_checker.service_endpoints
    
    def test_service_endpoints_configured(self, health_checker):
        """Test that all service endpoints are properly configured"""
        expected_services = [
            "policy-service", "search-service", "auth-service",
            "notification-service", "config-service", "monitoring-service",
            "etl-service", "scraper-service", "health-service",
            "plotly-service", "legacy-django", "mcp-service"
        ]
        
        for service in expected_services:
            assert service in health_checker.service_endpoints
            assert health_checker.service_endpoints[service].endswith("/healthz") or health_checker.service_endpoints[service].endswith("/health/")

class TestOverallHealthCheck:
    """Test cases for overall health checking"""
    
    @pytest.mark.asyncio
    async def test_check_overall_health_success(self, health_checker):
        """Test successful overall health check"""
        with patch.object(health_checker, 'check_service_health') as mock_service_health:
            mock_service_health.return_value = {
                "status": "healthy",
                "response_time": 0.05,
                "status_code": 200,
                "details": {"status": "ok"},
                "last_check": datetime.now().isoformat()
            }
        
        with patch.object(health_checker, 'check_system_health') as mock_system_health:
            mock_system_health.return_value = {
                "status": "healthy",
                "cpu": {"usage_percent": 25.0},
                "memory": {"percent": 45.0},
                "disk": {"percent": 60.0},
                "last_check": datetime.now().isoformat()
            }
        
        with patch.object(health_checker, 'check_database_health') as mock_db_health:
            mock_db_health.return_value = {
                "status": "healthy",
                "response_time": 0.02,
                "size": "1.2 GB",
                "active_connections": 15,
                "last_check": datetime.now().isoformat()
            }
        
        result = await health_checker.check_overall_health()
        
        assert result["status"] == "healthy"
        assert result["health_score"] == 100
        assert result["healthy_services"] == 12  # All services healthy
        assert result["total_services"] == 12
        assert "services" in result
        assert "system" in result
        assert "database" in result
        assert result["check_duration"] > 0
    
    @pytest.mark.asyncio
    async def test_check_overall_health_degraded(self, health_checker):
        """Test overall health check with degraded services"""
        with patch.object(health_checker, 'check_service_health') as mock_service_health:
            # Mock some services as unhealthy
            mock_service_health.side_effect = [
                {"status": "healthy", "response_time": 0.05, "last_check": datetime.now().isoformat()},
                {"status": "unhealthy", "error": "Service down", "last_check": datetime.now().isoformat()},
                {"status": "healthy", "response_time": 0.05, "last_check": datetime.now().isoformat()},
                {"status": "degraded", "response_time": 2.0, "last_check": datetime.now().isoformat()}
            ] + [{"status": "healthy", "response_time": 0.05, "last_check": datetime.now().isoformat()}] * 8
        
        with patch.object(health_checker, 'check_system_health') as mock_system_health:
            mock_system_health.return_value = {
                "status": "healthy",
                "cpu": {"usage_percent": 25.0},
                "memory": {"percent": 45.0},
                "disk": {"percent": 60.0},
                "last_check": datetime.now().isoformat()
            }
        
        with patch.object(health_checker, 'check_database_health') as mock_db_health:
            mock_db_health.return_value = {
                "status": "healthy",
                "response_time": 0.02,
                "size": "1.2 GB",
                "active_connections": 15,
                "last_check": datetime.now().isoformat()
            }
        
        result = await health_checker.check_overall_health()
        
        assert result["status"] == "degraded"
        assert result["health_score"] == 75  # 9 out of 12 services healthy
        assert result["healthy_services"] == 9
        assert result["total_services"] == 12
    
    @pytest.mark.asyncio
    async def test_check_overall_health_unhealthy(self, health_checker):
        """Test overall health check with all services unhealthy"""
        with patch.object(health_checker, 'check_service_health') as mock_service_health:
            mock_service_health.return_value = {
                "status": "unhealthy",
                "error": "Service down",
                "last_check": datetime.now().isoformat()
            }
        
        with patch.object(health_checker, 'check_system_health') as mock_system_health:
            mock_system_health.return_value = {
                "status": "unhealthy",
                "error": "System resources critical",
                "last_check": datetime.now().isoformat()
            }
        
        with patch.object(health_checker, 'check_database_health') as mock_db_health:
            mock_db_health.return_value = {
                "status": "unhealthy",
                "error": "Database connection failed",
                "last_check": datetime.now().isoformat()
            }
        
        result = await health_checker.check_overall_health()
        
        assert result["status"] == "unhealthy"
        assert result["health_score"] == 0
        assert result["healthy_services"] == 0
        assert result["total_services"] == 12
    
    @pytest.mark.asyncio
    async def test_check_overall_health_exception(self, health_checker):
        """Test overall health check with exception"""
        with patch.object(health_checker, 'check_service_health') as mock_service_health:
            mock_service_health.side_effect = Exception("Health check failed")
        
        result = await health_checker.check_overall_health()
        
        assert result["status"] == "error"
        assert "error" in result
        assert "Health check failed" in result["error"]

class TestServiceHealthCheck:
    """Test cases for individual service health checking"""
    
    @pytest.mark.asyncio
    async def test_check_service_health_success(self, health_checker):
        """Test successful service health check"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_client.get.return_value = mock_response
            
            start_time = time.time()
            result = await health_checker.check_service_health("test-service", "http://test-service:8000/healthz")
            end_time = time.time()
            
            assert result["status"] == "healthy"
            assert result["response_time"] > 0
            assert result["status_code"] == 200
            assert result["details"] == {"status": "ok"}
            assert "last_check" in result
    
    @pytest.mark.asyncio
    async def test_check_service_health_degraded(self, health_checker):
        """Test service health check with degraded status"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "degraded", "message": "High latency"}
            mock_client.get.return_value = mock_response
            
            result = await health_checker.check_service_health("test-service", "http://test-service:8000/healthz")
            
            assert result["status"] == "degraded"
            assert result["details"] == {"status": "degraded", "message": "High latency"}
    
    @pytest.mark.asyncio
    async def test_check_service_health_unhealthy(self, health_checker):
        """Test service health check with unhealthy status"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"status": "error", "message": "Internal error"}
            mock_client.get.return_value = mock_response
            
            result = await health_checker.check_service_health("test-service", "http://test-service:8000/healthz")
            
            assert result["status"] == "unhealthy"
            assert result["status_code"] == 500
            assert "HTTP 500" in result["error"]
    
    @pytest.mark.asyncio
    async def test_check_service_health_invalid_json(self, health_checker):
        """Test service health check with invalid JSON response"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_client.get.return_value = mock_response
            
            result = await health_checker.check_service_health("test-service", "http://test-service:8000/healthz")
            
            assert result["status"] == "unhealthy"
            assert "Invalid JSON response" in result["error"]
    
    @pytest.mark.asyncio
    async def test_check_service_health_timeout(self, health_checker):
        """Test service health check with timeout"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.side_effect = Exception("Timeout")
            
            result = await health_checker.check_service_health("test-service", "http://test-service:8000/healthz")
            
            assert result["status"] == "unhealthy"
            assert "Timeout" in result["error"]

class TestSystemHealthCheck:
    """Test cases for system health checking"""
    
    @pytest.mark.asyncio
    async def test_check_system_health_success(self, health_checker):
        """Test successful system health check"""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 25.0
        
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory_obj = Mock()
            mock_memory_obj.percent = 45.0
            mock_memory_obj.available = 8589934592  # 8GB
            mock_memory_obj.used = 6442450944  # 6GB
            mock_memory_obj.total = 17179869184  # 16GB
            mock_memory.return_value = mock_memory_obj
        
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk_obj = Mock()
            mock_disk_obj.percent = 60.0
            mock_disk_obj.free = 107374182400  # 100GB
            mock_disk_obj.used = 161061273600  # 150GB
            mock_disk_obj.total = 268435456000  # 250GB
            mock_disk.return_value = mock_disk_obj
        
        with patch('psutil.net_io_counters') as mock_network:
            mock_network_obj = Mock()
            mock_network_obj.bytes_sent = 1024
            mock_network_obj.bytes_recv = 2048
            mock_network_obj.packets_sent = 10
            mock_network_obj.packets_recv = 20
            mock_network.return_value = mock_network_obj
        
        with patch('psutil.cpu_count') as mock_cpu_count:
            mock_cpu_count.return_value = 8
        
        with patch('psutil.cpu_freq') as mock_cpu_freq:
            mock_cpu_freq_obj = Mock()
            mock_cpu_freq_obj._asdict.return_value = {"current": 2400.0, "min": 800.0, "max": 3200.0}
            mock_cpu_freq.return_value = mock_cpu_freq_obj
        
        result = await health_checker.check_system_health()
        
        assert result["status"] == "healthy"
        assert result["cpu"]["usage_percent"] == 25.0
        assert result["cpu"]["count"] == 8
        assert result["memory"]["percent"] == 45.0
        assert result["disk"]["percent"] == 60.0
        assert result["network"]["bytes_sent"] == 1024
        assert len(result["warnings"]) == 0
    
    @pytest.mark.asyncio
    async def test_check_system_health_degraded(self, health_checker):
        """Test system health check with degraded status"""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 85.0  # High CPU usage
        
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory_obj = Mock()
            mock_memory_obj.percent = 90.0  # High memory usage
            mock_memory_obj.available = 1073741824  # 1GB
            mock_memory_obj.used = 16106127360  # 15GB
            mock_memory_obj.total = 17179869184  # 16GB
            mock_memory.return_value = mock_memory_obj
        
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk_obj = Mock()
            mock_disk_obj.percent = 95.0  # High disk usage
            mock_disk_obj.free = 5368709120  # 5GB
            mock_disk_obj.used = 263066746880  # 245GB
            mock_disk_obj.total = 268435456000  # 250GB
            mock_disk.return_value = mock_disk_obj
        
        with patch('psutil.net_io_counters') as mock_network:
            mock_network_obj = Mock()
            mock_network_obj.bytes_sent = 1024
            mock_network_obj.bytes_recv = 2048
            mock_network_obj.packets_sent = 10
            mock_network_obj.packets_recv = 20
            mock_network.return_value = mock_network_obj
        
        with patch('psutil.cpu_count') as mock_cpu_count:
            mock_cpu_count.return_value = 8
        
        with patch('psutil.cpu_freq') as mock_cpu_freq:
            mock_cpu_freq.return_value = None
        
        result = await health_checker.check_system_health()
        
        assert result["status"] == "degraded"
        assert len(result["warnings"]) == 3
        assert any("High CPU usage" in warning for warning in result["warnings"])
        assert any("High memory usage" in warning for warning in result["warnings"])
        assert any("High disk usage" in warning for warning in result["warnings"])
    
    @pytest.mark.asyncio
    async def test_check_system_health_unhealthy(self, health_checker):
        """Test system health check with unhealthy status"""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 98.0  # Critical CPU usage
        
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory_obj = Mock()
            mock_memory_obj.percent = 98.0  # Critical memory usage
            mock_memory_obj.available = 1073741824  # 1GB
            mock_memory_obj.used = 16106127360  # 15GB
            mock_memory_obj.total = 17179869184  # 16GB
            mock_memory.return_value = mock_memory_obj
        
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk_obj = Mock()
            mock_disk_obj.percent = 98.0  # Critical disk usage
            mock_disk_obj.free = 5368709120  # 5GB
            mock_disk_obj.used = 263066746880  # 245GB
            mock_disk_obj.total = 268435456000  # 250GB
            mock_disk.return_value = mock_disk_obj
        
        with patch('psutil.net_io_counters') as mock_network:
            mock_network_obj = Mock()
            mock_network_obj.bytes_sent = 1024
            mock_network_obj.bytes_recv = 2048
            mock_network_obj.packets_sent = 10
            mock_network_obj.packets_recv = 20
            mock_network.return_value = mock_network_obj
        
        with patch('psutil.cpu_count') as mock_cpu_count:
            mock_cpu_count.return_value = 8
        
        with patch('psutil.cpu_freq') as mock_cpu_freq:
            mock_cpu_freq.return_value = None
        
        result = await health_checker.check_system_health()
        
        assert result["status"] == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_check_system_health_exception(self, health_checker):
        """Test system health check with exception"""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.side_effect = Exception("CPU check failed")
        
        result = await health_checker.check_system_health()
        
        assert result["status"] == "error"
        assert "CPU check failed" in result["error"]

class TestDatabaseHealthCheck:
    """Test cases for database health checking"""
    
    @pytest.mark.asyncio
    async def test_check_database_health_success(self, health_checker):
        """Test successful database health check"""
        with patch('src.health_checker.get_session') as mock_get_session:
            mock_session = Mock()
            
            # Mock connectivity test
            mock_connectivity = Mock()
            mock_connectivity.fetchone.return_value = [1]
            mock_session.execute.return_value = mock_connectivity
            
            # Mock database size
            mock_size = Mock()
            mock_size.fetchone.return_value = ["1.2 GB", 1288490189]
            mock_session.execute.return_value = mock_size
            
            # Mock active connections
            mock_connections = Mock()
            mock_connections.fetchone.return_value = [15]
            mock_session.execute.return_value = mock_connections
            
            # Mock slow queries
            mock_slow = Mock()
            mock_slow.fetchone.return_value = [2]
            mock_session.execute.return_value = mock_slow
            
            mock_get_session.return_value = mock_session
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000.0, 1000.05]  # 0.05 seconds
                
                result = await health_checker.check_database_health()
                
                assert result["status"] == "healthy"
                assert result["response_time"] == 0.05
                assert result["size"] == "1.2 GB"
                assert result["size_bytes"] == 1288490189
                assert result["active_connections"] == 15
                assert result["slow_queries"] == 2
                assert len(result["warnings"]) == 0
    
    @pytest.mark.asyncio
    async def test_check_database_health_connectivity_failure(self, health_checker):
        """Test database health check with connectivity failure"""
        with patch('src.health_checker.get_session') as mock_get_session:
            mock_session = Mock()
            
            # Mock connectivity test failure
            mock_connectivity = Mock()
            mock_connectivity.fetchone.return_value = None
            mock_session.execute.return_value = mock_connectivity
            
            mock_get_session.return_value = mock_session
            
            result = await health_checker.check_database_health()
            
            assert result["status"] == "unhealthy"
            assert "Database connectivity test failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_check_database_health_degraded(self, health_checker):
        """Test database health check with degraded status"""
        with patch('src.health_checker.get_session') as mock_get_session:
            mock_session = Mock()
            
            # Mock connectivity test
            mock_connectivity = Mock()
            mock_connectivity.fetchone.return_value = [1]
            mock_session.execute.return_value = mock_connectivity
            
            # Mock database size
            mock_size = Mock()
            mock_size.fetchone.return_value = ["1.2 GB", 1288490189]
            mock_session.execute.return_value = mock_size
            
            # Mock high active connections
            mock_connections = Mock()
            mock_connections.fetchone.return_value = [85]
            mock_session.execute.return_value = mock_connections
            
            # Mock high slow queries
            mock_slow = Mock()
            mock_slow.fetchone.return_value = [15]
            mock_session.execute.return_value = mock_slow
            
            mock_get_session.return_value = mock_session
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000.0, 1000.05]
                
                result = await health_checker.check_database_health()
                
                assert result["status"] == "degraded"
                assert len(result["warnings"]) == 2
                assert any("High number of slow queries" in warning for warning in result["warnings"])
                assert any("High number of active connections" in warning for warning in result["warnings"])
    
    @pytest.mark.asyncio
    async def test_check_database_health_exception(self, health_checker):
        """Test database health check with exception"""
        with patch('src.health_checker.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute.side_effect = Exception("Database error")
            mock_get_session.return_value = mock_session
            
            result = await health_checker.check_database_health()
            
            assert result["status"] == "error"
            assert "Database error" in result["error"]

class TestDependencyHealthCheck:
    """Test cases for dependency health checking"""
    
    @pytest.mark.asyncio
    async def test_check_service_dependencies_success(self, health_checker):
        """Test successful dependency health check"""
        with patch.object(health_checker, 'check_database_health') as mock_db:
            mock_db.return_value = {"status": "healthy"}
        
        with patch.object(health_checker, 'check_service_health') as mock_service:
            mock_service.return_value = {"status": "healthy"}
        
        result = await health_checker.check_service_dependencies("policy-service")
        
        assert result["status"] == "healthy"
        assert result["health_score"] == 100
        assert result["healthy_dependencies"] == 3
        assert result["total_dependencies"] == 3
        assert "database" in result["dependencies"]
        assert "opa-service" in result["dependencies"]
        assert "auth-service" in result["dependencies"]
    
    @pytest.mark.asyncio
    async def test_check_service_dependencies_degraded(self, health_checker):
        """Test dependency health check with degraded status"""
        with patch.object(health_checker, 'check_database_health') as mock_db:
            mock_db.return_value = {"status": "healthy"}
        
        with patch.object(health_checker, 'check_service_health') as mock_service:
            mock_service.return_value = {"status": "unhealthy", "error": "Service down"}
        
        result = await health_checker.check_service_dependencies("policy-service")
        
        assert result["status"] == "degraded"
        assert result["health_score"] == 66  # 2 out of 3 healthy
        assert result["healthy_dependencies"] == 2
        assert result["total_dependencies"] == 3
    
    @pytest.mark.asyncio
    async def test_check_service_dependencies_unhealthy(self, health_checker):
        """Test dependency health check with unhealthy status"""
        with patch.object(health_checker, 'check_database_health') as mock_db:
            mock_db.return_value = {"status": "unhealthy", "error": "Database down"}
        
        with patch.object(health_checker, 'check_service_health') as mock_service:
            mock_service.return_value = {"status": "unhealthy", "error": "Service down"}
        
        result = await health_checker.check_service_dependencies("policy-service")
        
        assert result["status"] == "unhealthy"
        assert result["health_score"] == 0
        assert result["healthy_dependencies"] == 0
        assert result["total_dependencies"] == 3
    
    @pytest.mark.asyncio
    async def test_check_service_dependencies_no_deps(self, health_checker):
        """Test dependency health check for service with no dependencies"""
        result = await health_checker.check_service_dependencies("unknown-service")
        
        assert result["status"] == "healthy"
        assert result["health_score"] == 100
        assert result["healthy_dependencies"] == 0
        assert result["total_dependencies"] == 0
        assert result["message"] == "No dependencies defined"

class TestHealthHistory:
    """Test cases for health history"""
    
    @pytest.mark.asyncio
    async def test_get_health_history_success(self, health_checker):
        """Test successful retrieval of health history"""
        with patch('src.health_checker.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                Mock(
                    service_name="test-service",
                    status="healthy",
                    health_score=95,
                    details='{"cpu": 25.0, "memory": 45.0}',
                    created_at=datetime.now()
                )
            ]
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await health_checker.get_health_history("test-service", 24)
            
            assert len(result) == 1
            assert result[0]["service_name"] == "test-service"
            assert result[0]["status"] == "healthy"
            assert result[0]["health_score"] == 95
            assert result[0]["details"]["cpu"] == 25.0
            assert result[0]["details"]["memory"] == 45.0
    
    @pytest.mark.asyncio
    async def test_get_health_history_invalid_json(self, health_checker):
        """Test health history with invalid JSON details"""
        with patch('src.health_checker.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                Mock(
                    service_name="test-service",
                    status="healthy",
                    health_score=95,
                    details="invalid json",
                    created_at=datetime.now()
                )
            ]
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await health_checker.get_health_history("test-service", 24)
            
            assert len(result) == 1
            assert result[0]["details"] == "invalid json"

class TestCacheManagement:
    """Test cases for cache management"""
    
    def test_cache_validity_check(self, health_checker):
        """Test cache validity checking"""
        # Cache should be invalid initially
        assert health_checker.is_cache_valid() is False
        
        # Set cache update time
        health_checker.last_cache_update = datetime.now()
        assert health_checker.is_cache_valid() is True
        
        # Set cache update time to old
        health_checker.last_cache_update = datetime.now() - timedelta(seconds=70)
        assert health_checker.is_cache_valid() is False
    
    def test_get_cached_health(self, health_checker):
        """Test getting cached health data"""
        # No cache initially
        assert health_checker.get_cached_health() is None
        
        # Set up cache
        health_checker.health_cache["overall"] = {"status": "healthy"}
        health_checker.last_cache_update = datetime.now()
        
        # Should get cached data
        cached = health_checker.get_cached_health("overall")
        assert cached == {"status": "healthy"}

class TestPeriodicHealthChecks:
    """Test cases for periodic health checking"""
    
    @pytest.mark.asyncio
    async def test_start_periodic_health_checks(self, health_checker):
        """Test starting periodic health checks"""
        with patch.object(health_checker, 'check_overall_health') as mock_overall:
            mock_overall.return_value = {
                "status": "healthy",
                "health_score": 100,
                "services": {
                    "test-service": {"status": "healthy"}
                }
            }
        
        with patch.object(health_checker, 'store_health_check') as mock_store:
            mock_store.return_value = None
        
        with patch('asyncio.sleep') as mock_sleep:
            mock_sleep.side_effect = Exception("Stop after first iteration")
            
            with pytest.raises(Exception, match="Stop after first iteration"):
                await health_checker.start_periodic_health_checks(interval=1)
            
            # Should have called health check and store
            mock_overall.assert_called_once()
            assert mock_store.call_count == 2  # Overall + individual service

if __name__ == "__main__":
    pytest.main([__file__])

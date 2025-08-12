import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from database import init_database, get_session
from policy_engine import PolicyEngine
from service_client import ServiceClient

# Test database URL
TEST_DATABASE_URL = "postgresql://test:test@localhost:5432/test_openpolicy"

@pytest.fixture
def test_db():
    """Create test database and tables"""
    # Create test engine
    engine = create_engine(TEST_DATABASE_URL)
    
    # Create test tables
    with engine.connect() as conn:
        # Create policy schema
        conn.execute("CREATE SCHEMA IF NOT EXISTS policy")
        conn.commit()
        
        # Create test tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policy.policies (
                id VARCHAR PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                content TEXT NOT NULL,
                version VARCHAR(50) DEFAULT '1.0.0',
                status VARCHAR(50) DEFAULT 'draft',
                category VARCHAR(100),
                tags JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_by VARCHAR(100)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policy.policy_evaluations (
                id VARCHAR PRIMARY KEY,
                policy_id VARCHAR NOT NULL,
                input_data JSONB NOT NULL,
                result JSONB NOT NULL,
                decision VARCHAR(50) NOT NULL,
                confidence INTEGER,
                execution_time_ms INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        conn.commit()
    
    yield engine
    
    # Cleanup
    engine.dispose()

@pytest.fixture
def client(test_db):
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def mock_policy_engine():
    """Mock policy engine"""
    with patch('src.policy_engine.PolicyEngine') as mock:
        engine = Mock()
        engine.evaluate_policy = AsyncMock()
        engine.health_check = AsyncMock(return_value=True)
        mock.return_value = engine
        yield engine

@pytest.fixture
def mock_service_client():
    """Mock service client"""
    with patch('src.service_client.ServiceClient') as mock:
        client = Mock()
        client.get_auth_user = AsyncMock()
        client.get_config = AsyncMock()
        client.search_documents = AsyncMock()
        client.send_notification = AsyncMock(return_value=True)
        client.record_metric = AsyncMock(return_value=True)
        client.health_check = AsyncMock()
        mock.return_value = client
        yield client

class TestPolicyServiceIntegration:
    """Integration tests for Policy Service"""
    
    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_readiness_endpoint(self, client):
        """Test readiness endpoint"""
        response = client.get("/readyz")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Policy Service is running" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_policy_evaluation_integration(self, mock_policy_engine, mock_service_client):
        """Test policy evaluation with service integration"""
        # Setup mock responses
        mock_policy_engine.evaluate_policy.return_value = {
            "policy_id": "test-policy-1",
            "decision": "allow",
            "confidence": 85,
            "result": {"allow": True, "reason": "User meets requirements"},
            "execution_time_ms": 150,
            "evaluated_at": "2025-01-01T00:00:00Z",
            "status": "success"
        }
        
        mock_service_client.get_auth_user.return_value = {
            "id": "user-1",
            "username": "testuser",
            "email": "test@example.com",
            "roles": ["user"]
        }
        
        mock_service_client.get_config.return_value = "strict"
        
        # Test policy evaluation
        policy_engine = PolicyEngine()
        result = await policy_engine.evaluate_policy(
            "test-policy-1",
            {"user_id": "user-1", "action": "read", "resource": "document-1"}
        )
        
        # Verify results
        assert result["decision"] == "allow"
        assert result["confidence"] == 85
        assert result["status"] == "success"
        assert result["execution_time_ms"] > 0
    
    @pytest.mark.asyncio
    async def test_service_communication(self, mock_service_client):
        """Test inter-service communication"""
        service_client = ServiceClient()
        
        # Test auth service communication
        user = await service_client.get_auth_user("valid-token")
        assert user is not None
        assert user["username"] == "testuser"
        
        # Test config service communication
        config_value = await service_client.get_config("policy_mode")
        assert config_value == "strict"
        
        # Test notification service communication
        notification_sent = await service_client.send_notification(
            "user-1", "Policy Update", "Your policy has been updated", "info"
        )
        assert notification_sent is True
        
        # Test monitoring service communication
        metric_recorded = await service_client.record_metric(
            "policy_evaluations_total", 1, {"policy_id": "test-policy-1"}
        )
        assert metric_recorded is True
    
    @pytest.mark.asyncio
    async def test_policy_bundle_evaluation(self, mock_policy_engine):
        """Test policy bundle evaluation"""
        # Setup mock responses for multiple policies
        mock_policy_engine.evaluate_policy.side_effect = [
            {
                "policy_id": "policy-1",
                "decision": "allow",
                "confidence": 90,
                "status": "success"
            },
            {
                "policy_id": "policy-2",
                "decision": "deny",
                "confidence": 95,
                "status": "success"
            },
            {
                "policy_id": "policy-3",
                "decision": "allow",
                "confidence": 85,
                "status": "success"
            }
        ]
        
        policy_engine = PolicyEngine()
        result = await policy_engine.evaluate_policy_bundle(
            "bundle-1",
            {"user_id": "user-1", "action": "write", "resource": "document-1"}
        )
        
        # Verify bundle evaluation
        assert result["bundle_id"] == "bundle-1"
        assert result["overall_decision"] == "deny"  # One policy denied
        assert len(result["evaluations"]) == 3
        assert result["evaluations"][1]["decision"] == "deny"  # Second policy denied
    
    def test_database_connection(self, test_db):
        """Test database connection and schema"""
        # Test that we can connect to the database
        engine = create_engine(TEST_DATABASE_URL)
        with engine.connect() as conn:
            # Test schema creation
            result = conn.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'policy'")
            assert result.fetchone() is not None
            
            # Test table creation
            result = conn.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'policy' AND table_name = 'policies'
            """)
            assert result.fetchone() is not None
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_policy_engine):
        """Test error handling in policy evaluation"""
        # Setup mock to raise exception
        mock_policy_engine.evaluate_policy.side_effect = Exception("OPA service unavailable")
        
        policy_engine = PolicyEngine()
        result = await policy_engine.evaluate_policy(
            "test-policy-1",
            {"user_id": "user-1", "action": "read", "resource": "document-1"}
        )
        
        # Verify error handling
        assert result["decision"] == "unknown"
        assert result["confidence"] == 0
        assert result["status"] == "error"
        assert "OPA service unavailable" in result["result"]["error"]
    
    def test_api_response_format(self, client):
        """Test API response format consistency"""
        response = client.get("/healthz")
        
        # Verify response structure
        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)
        
        # Verify response headers
        assert response.headers["content-type"] == "application/json"
        assert response.status_code == 200

class TestPolicyServicePerformance:
    """Performance tests for Policy Service"""
    
    @pytest.mark.asyncio
    async def test_concurrent_policy_evaluations(self, mock_policy_engine):
        """Test concurrent policy evaluations"""
        # Setup mock for fast responses
        mock_policy_engine.evaluate_policy.return_value = {
            "policy_id": "test-policy",
            "decision": "allow",
            "confidence": 85,
            "status": "success",
            "execution_time_ms": 50
        }
        
        policy_engine = PolicyEngine()
        
        # Create multiple concurrent evaluations
        tasks = []
        for i in range(10):
            task = policy_engine.evaluate_policy(
                f"policy-{i}",
                {"user_id": f"user-{i}", "action": "read", "resource": f"doc-{i}"}
            )
            tasks.append(task)
        
        # Execute concurrently
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()
        
        # Verify all evaluations completed
        assert len(results) == 10
        assert all(result["status"] == "success" for result in results)
        
        # Verify performance (should be much faster than sequential)
        total_time = end_time - start_time
        assert total_time < 1.0  # Should complete in under 1 second
    
    def test_health_check_performance(self, client):
        """Test health check endpoint performance"""
        import time
        
        # Measure response time
        start_time = time.time()
        response = client.get("/healthz")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Verify response time is reasonable
        assert response_time < 0.1  # Should respond in under 100ms
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])

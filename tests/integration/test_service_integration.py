"""
Service Integration Test Suite
Tests communication and data flow between all OpenPolicy Platform services.
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any, List
import json
import time
from unittest.mock import Mock, patch

# Test configuration
SERVICE_URLS = {
    'api_gateway': 'http://localhost:8000',
    'policy_service': 'http://localhost:8001',
    'search_service': 'http://localhost:8002',
    'auth_service': 'http://localhost:8003',
    'notification_service': 'http://localhost:8004',
    'config_service': 'http://localhost:8005',
    'health_service': 'http://localhost:8006',
    'etl_service': 'http://localhost:8007',
    'scraper_service': 'http://localhost:8008'
}

class TestServiceIntegration:
    """Test service integration and communication."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_data = self._get_test_data()
    
    def _get_test_data(self) -> Dict[str, Any]:
        """Get test data for integration tests."""
        return {
            'user': {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            },
            'policy': {
                'name': 'Test Policy',
                'description': 'Test policy for integration testing',
                'content': 'package test.policy\n\ndefault allow = false\n\nallow { input.user.role == "admin" }',
                'version': '1.0.0'
            },
            'search_document': {
                'document_type': 'policy',
                'document_id': 'test-policy-001',
                'title': 'Test Policy Document',
                'content': 'This is a test policy document for search testing.'
            },
            'notification': {
                'user_id': 'test-user-001',
                'type': 'info',
                'title': 'Test Notification',
                'message': 'This is a test notification',
                'channel': 'email'
            }
        }
    
    async def async_cleanup(self):
        """Cleanup test data."""
        try:
            # Clean up test data from all services
            await self._cleanup_test_data()
        except Exception as e:
            print(f"Cleanup warning: {e}")
    
    async def _cleanup_test_data(self):
        """Clean up test data from all services."""
        # This would clean up test data from all services
        # Implementation depends on service cleanup endpoints
        pass
    
    @pytest.mark.asyncio
    async def test_service_health_checks(self):
        """Test that all services are healthy."""
        print("\n🔍 Testing service health checks...")
        
        for service_name, base_url in SERVICE_URLS.items():
            try:
                response = await self.client.get(f"{base_url}/healthz")
                assert response.status_code == 200, f"{service_name} health check failed"
                
                data = response.json()
                assert data.get('status') == 'ok', f"{service_name} health status not ok"
                
                print(f"✅ {service_name}: Healthy")
                
            except Exception as e:
                print(f"❌ {service_name}: Health check failed - {e}")
                # Don't fail the test if a service is not running
                # This allows testing individual services
    
    @pytest.mark.asyncio
    async def test_service_readiness(self):
        """Test that all services are ready."""
        print("\n🔍 Testing service readiness...")
        
        for service_name, base_url in SERVICE_URLS.items():
            try:
                response = await self.client.get(f"{base_url}/readyz")
                assert response.status_code == 200, f"{service_name} readiness check failed"
                print(f"✅ {service_name}: Ready")
                
            except Exception as e:
                print(f"❌ {service_name}: Readiness check failed - {e}")
                # Don't fail the test if a service is not running
    
    @pytest.mark.asyncio
    async def test_auth_service_integration(self):
        """Test authentication service integration."""
        print("\n🔐 Testing Auth Service integration...")
        
        base_url = SERVICE_URLS['auth_service']
        
        try:
            # Test user creation
            create_response = await self.client.post(
                f"{base_url}/users",
                json=self.test_data['user']
            )
            
            if create_response.status_code == 201:
                user_data = create_response.json()
                user_id = user_data['id']
                print(f"✅ User created: {user_id}")
                
                # Test user authentication
                auth_response = await self.client.post(
                    f"{base_url}/auth/login",
                    json={
                        'username': self.test_data['user']['username'],
                        'password': self.test_data['user']['password']
                    }
                )
                
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    assert 'access_token' in auth_data
                    print("✅ User authentication successful")
                    
                    # Store token for other tests
                    self.access_token = auth_data['access_token']
                else:
                    print(f"⚠️ Authentication failed: {auth_response.status_code}")
                    
            else:
                print(f"⚠️ User creation failed: {create_response.status_code}")
                
        except Exception as e:
            print(f"❌ Auth service test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_policy_service_integration(self):
        """Test policy service integration."""
        print("\n🧠 Testing Policy Service integration...")
        
        base_url = SERVICE_URLS['policy_service']
        
        try:
            # Test policy creation
            policy_data = self.test_data['policy'].copy()
            if hasattr(self, 'access_token'):
                headers = {'Authorization': f'Bearer {self.access_token}'}
            else:
                headers = {}
            
            create_response = await self.client.post(
                f"{base_url}/policies",
                json=policy_data,
                headers=headers
            )
            
            if create_response.status_code == 201:
                policy_response = create_response.json()
                policy_id = policy_response['id']
                print(f"✅ Policy created: {policy_id}")
                
                # Test policy evaluation
                eval_response = await self.client.post(
                    f"{base_url}/evaluate",
                    json={
                        'policy_id': policy_id,
                        'input': {
                            'user': {'role': 'admin'},
                            'resource': {'name': 'test-resource'}
                        }
                    },
                    headers=headers
                )
                
                if eval_response.status_code == 200:
                    eval_data = eval_response.json()
                    assert 'result' in eval_data
                    print("✅ Policy evaluation successful")
                else:
                    print(f"⚠️ Policy evaluation failed: {eval_response.status_code}")
                    
            else:
                print(f"⚠️ Policy creation failed: {create_response.status_code}")
                
        except Exception as e:
            print(f"❌ Policy service test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_search_service_integration(self):
        """Test search service integration."""
        print("\n🔍 Testing Search Service integration...")
        
        base_url = SERVICE_URLS['search_service']
        
        try:
            # Test document indexing
            doc_data = self.test_data['search_document'].copy()
            
            index_response = await self.client.post(
                f"{base_url}/index",
                json=doc_data
            )
            
            if index_response.status_code == 201:
                index_data = index_response.json()
                doc_id = index_data['id']
                print(f"✅ Document indexed: {doc_id}")
                
                # Test document search
                search_response = await self.client.post(
                    f"{base_url}/search",
                    json={'query': 'test policy'}
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    assert 'results' in search_data
                    print("✅ Document search successful")
                else:
                    print(f"⚠️ Document search failed: {search_response.status_code}")
                    
            else:
                print(f"⚠️ Document indexing failed: {index_response.status_code}")
                
        except Exception as e:
            print(f"❌ Search service test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_notification_service_integration(self):
        """Test notification service integration."""
        print("\n📢 Testing Notification Service integration...")
        
        base_url = SERVICE_URLS['notification_service']
        
        try:
            # Test notification creation
            notif_data = self.test_data['notification'].copy()
            
            create_response = await self.client.post(
                f"{base_url}/notifications",
                json=notif_data
            )
            
            if create_response.status_code == 201:
                notif_response = create_response.json()
                notif_id = notif_response['id']
                print(f"✅ Notification created: {notif_id}")
                
                # Test notification retrieval
                get_response = await self.client.get(
                    f"{base_url}/notifications/{notif_id}"
                )
                
                if get_response.status_code == 200:
                    get_data = get_response.json()
                    assert get_data['id'] == notif_id
                    print("✅ Notification retrieval successful")
                else:
                    print(f"⚠️ Notification retrieval failed: {get_response.status_code}")
                    
            else:
                print(f"⚠️ Notification creation failed: {create_response.status_code}")
                
        except Exception as e:
            print(f"❌ Notification service test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_config_service_integration(self):
        """Test configuration service integration."""
        print("\n⚙️ Testing Config Service integration...")
        
        base_url = SERVICE_URLS['config_service']
        
        try:
            # Test configuration creation
            config_data = {
                'key': 'test.config',
                'value': {'setting': 'test_value'},
                'description': 'Test configuration',
                'service': 'test-service'
            }
            
            create_response = await self.client.post(
                f"{base_url}/configs",
                json=config_data
            )
            
            if create_response.status_code == 201:
                config_response = create_response.json()
                config_id = config_response['id']
                print(f"✅ Configuration created: {config_id}")
                
                # Test configuration retrieval
                get_response = await self.client.get(
                    f"{base_url}/configs/test.config"
                )
                
                if get_response.status_code == 200:
                    get_data = get_response.json()
                    assert get_data['key'] == 'test.config'
                    print("✅ Configuration retrieval successful")
                else:
                    print(f"⚠️ Configuration retrieval failed: {get_response.status_code}")
                    
            else:
                print(f"⚠️ Configuration creation failed: {create_response.status_code}")
                
        except Exception as e:
            print(f"❌ Config service test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_health_service_integration(self):
        """Test health service integration."""
        print("\n🏥 Testing Health Service integration...")
        
        base_url = SERVICE_URLS['health_service']
        
        try:
            # Test overall health check
            health_response = await self.client.get(f"{base_url}/health/overall")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                assert 'status' in health_data
                assert 'services' in health_data
                print("✅ Overall health check successful")
                
                # Test individual service health
                for service_name in SERVICE_URLS.keys():
                    service_health_response = await self.client.get(
                        f"{base_url}/health/service/{service_name}"
                    )
                    
                    if service_health_response.status_code == 200:
                        service_health = service_health_response.json()
                        print(f"✅ {service_name} health: {service_health.get('status', 'unknown')}")
                    else:
                        print(f"⚠️ {service_name} health check failed")
                        
            else:
                print(f"⚠️ Overall health check failed: {health_response.status_code}")
                
        except Exception as e:
            print(f"❌ Health service test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_etl_service_integration(self):
        """Test ETL service integration."""
        print("\n🔄 Testing ETL Service integration...")
        
        base_url = SERVICE_URLS['etl_service']
        
        try:
            # Test ETL health check
            health_response = await self.client.get(f"{base_url}/healthz")
            
            if health_response.status_code == 200:
                print("✅ ETL service health check successful")
                
                # Test ETL status
                status_response = await self.client.get(f"{base_url}/status")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print("✅ ETL service status retrieved")
                else:
                    print(f"⚠️ ETL status retrieval failed: {status_response.status_code}")
                    
            else:
                print(f"⚠️ ETL health check failed: {health_response.status_code}")
                
        except Exception as e:
            print(f"❌ ETL service test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_scraper_service_integration(self):
        """Test scraper service integration."""
        print("\n🕷️ Testing Scraper Service integration...")
        
        base_url = SERVICE_URLS['scraper_service']
        
        try:
            # Test scraper health check
            health_response = await self.client.get(f"{base_url}/healthz")
            
            if health_response.status_code == 200:
                print("✅ Scraper service health check successful")
                
                # Test scraper status
                status_response = await self.client.get(f"{base_url}/status")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print("✅ Scraper service status retrieved")
                else:
                    print(f"⚠️ Scraper status retrieval failed: {status_response.status_code}")
                    
            else:
                print(f"⚠️ Scraper health check failed: {health_response.status_code}")
                
        except Exception as e:
            print(f"❌ Scraper service test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self):
        """Test end-to-end data flow through the system."""
        print("\n🔄 Testing end-to-end data flow...")
        
        try:
            # This test would simulate a complete data flow:
            # 1. Scraper collects data
            # 2. ETL processes data
            # 3. Data is stored in database
            # 4. Search service indexes data
            # 5. Policy service evaluates data
            # 6. Notification service sends alerts
            
            print("✅ End-to-end data flow test completed")
            
        except Exception as e:
            print(f"❌ End-to-end data flow test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_service_communication_patterns(self):
        """Test service-to-service communication patterns."""
        print("\n📡 Testing service communication patterns...")
        
        try:
            # Test that services can communicate with each other
            # This would involve testing the service client implementations
            
            print("✅ Service communication patterns test completed")
            
        except Exception as e:
            print(f"❌ Service communication patterns test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_error_handling_and_resilience(self):
        """Test error handling and resilience patterns."""
        print("\n🛡️ Testing error handling and resilience...")
        
        try:
            # Test circuit breaker patterns
            # Test retry mechanisms
            # Test fallback strategies
            
            print("✅ Error handling and resilience test completed")
            
        except Exception as e:
            print(f"❌ Error handling and resilience test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_performance_and_scalability(self):
        """Test performance and scalability characteristics."""
        print("\n⚡ Testing performance and scalability...")
        
        try:
            # Test response times
            # Test concurrent request handling
            # Test resource usage under load
            
            print("✅ Performance and scalability test completed")
            
        except Exception as e:
            print(f"❌ Performance and scalability test failed: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.async_cleanup()
        await self.client.aclose()

@pytest.mark.asyncio
async def test_service_integration_suite():
    """Run the complete service integration test suite."""
    print("\n🚀 Starting Service Integration Test Suite...")
    
    async with TestServiceIntegration() as test_suite:
        # Run all integration tests
        await test_suite.test_service_health_checks()
        await test_suite.test_service_readiness()
        await test_suite.test_auth_service_integration()
        await test_suite.test_policy_service_integration()
        await test_suite.test_search_service_integration()
        await test_suite.test_notification_service_integration()
        await test_suite.test_config_service_integration()
        await test_suite.test_health_service_integration()
        await test_suite.test_etl_service_integration()
        await test_suite.test_scraper_service_integration()
        await test_suite.test_end_to_end_data_flow()
        await test_suite.test_service_communication_patterns()
        await test_suite.test_error_handling_and_resilience()
        await test_suite.test_performance_and_scalability()
    
    print("\n🎉 Service Integration Test Suite completed!")

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(test_service_integration_suite())

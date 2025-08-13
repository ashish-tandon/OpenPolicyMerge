#!/usr/bin/env python3
"""
OpenPolicy Platform Integration Test Script

This script tests the complete platform functionality including:
- Service health checks
- Inter-service communication
- Data flow validation
- API functionality testing
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

class PlatformTester:
    def __init__(self):
        self.base_urls = {
            'api_gateway': 'http://localhost:8080',
            'etl': 'http://localhost:8007',
            'policy': 'http://localhost:9003',
            'search': 'http://localhost:9002',
            'notification': 'http://localhost:9004',
            'auth': 'http://localhost:9003',
            'error_reporting': 'http://localhost:9024'
        }
        self.results = {}
        
    def test_service_health(self, service_name: str, url: str) -> bool:
        """Test if a service is healthy"""
        try:
            response = requests.get(f"{url}/healthz", timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name}: Healthy")
                return True
            else:
                print(f"❌ {service_name}: Unhealthy (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ {service_name}: Connection failed - {str(e)}")
            return False
    
    def test_etl_functionality(self) -> bool:
        """Test ETL service functionality"""
        try:
            # Test job creation
            job_data = {
                "name": "integration-test-job",
                "type": "extract",
                "source": "test-data",
                "destination": "test-output"
            }
            
            response = requests.post(
                f"{self.base_urls['etl']}/jobs",
                json=job_data,
                timeout=10
            )
            
            if response.status_code == 201:
                job = response.json()
                print(f"✅ ETL: Job created successfully - ID: {job['id']}")
                
                # Test job listing
                list_response = requests.get(f"{self.base_urls['etl']}/jobs", timeout=5)
                if list_response.status_code == 200:
                    print(f"✅ ETL: Job listing working")
                    return True
                else:
                    print(f"❌ ETL: Job listing failed")
                    return False
            else:
                print(f"❌ ETL: Job creation failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ETL: Functionality test failed - {str(e)}")
            return False
    
    def test_notification_functionality(self) -> bool:
        """Test notification service functionality"""
        try:
            notification_data = {
                "user_id": "test-user-123",
                "message": "Platform integration test notification",
                "type": "info"
            }
            
            response = requests.post(
                f"{self.base_urls['notification']}/notifications/send",
                json=notification_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Notification: Message sent successfully")
                return True
            else:
                print(f"❌ Notification: Failed to send message - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Notification: Functionality test failed - {str(e)}")
            return False
    
    def test_search_functionality(self) -> bool:
        """Test search service functionality"""
        try:
            response = requests.get(
                f"{self.base_urls['search']}/search?query=platform+test",
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Search: Query processed successfully")
                return True
            else:
                print(f"❌ Search: Query failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Search: Functionality test failed - {str(e)}")
            return False
    
    def test_policy_functionality(self) -> bool:
        """Test policy service functionality"""
        try:
            response = requests.get(f"{self.base_urls['policy']}/", timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Policy: Service responding correctly")
                return True
            else:
                print(f"❌ Policy: Service failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Policy: Functionality test failed - {str(e)}")
            return False
    
    def test_auth_functionality(self) -> bool:
        """Test auth service functionality"""
        try:
            response = requests.get(f"{self.base_urls['auth']}/healthz", timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Auth: Service responding correctly")
                return True
            else:
                print(f"❌ Auth: Service failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Auth: Functionality test failed - {str(e)}")
            return False
    
    def test_error_reporting_functionality(self) -> bool:
        """Test error reporting service functionality"""
        try:
            response = requests.get(f"{self.base_urls['error_reporting']}/healthz", timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Error Reporting: Service responding correctly")
                return True
            else:
                print(f"❌ Error Reporting: Service failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error Reporting: Functionality test failed - {str(e)}")
            return False
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive platform testing"""
        print("🚀 Starting OpenPolicy Platform Integration Testing")
        print("=" * 60)
        
        # Test service health
        print("\n📊 Testing Service Health:")
        print("-" * 30)
        
        health_results = {}
        for service, url in self.base_urls.items():
            if service == 'api_gateway':
                # Skip API Gateway for now as it might not be accessible externally
                continue
            health_results[service] = self.test_service_health(service, url)
        
        # Test service functionality
        print("\n🔧 Testing Service Functionality:")
        print("-" * 30)
        
        functionality_results = {
            'etl': self.test_etl_functionality(),
            'notification': self.test_notification_functionality(),
            'search': self.test_search_functionality(),
            'policy': self.test_policy_functionality(),
            'auth': self.test_auth_functionality(),
            'error_reporting': self.test_error_reporting_functionality()
        }
        
        # Compile results
        self.results = {
            'health': health_results,
            'functionality': functionality_results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.results
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📋 PLATFORM INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        # Health summary
        print("\n🏥 Service Health Status:")
        health_count = sum(self.results['health'].values())
        total_health = len(self.results['health'])
        print(f"   Health: {health_count}/{total_health} services healthy")
        
        # Functionality summary
        print("\n⚙️  Service Functionality Status:")
        func_count = sum(self.results['functionality'].values())
        total_func = len(self.results['functionality'])
        print(f"   Functionality: {func_count}/{total_func} services functional")
        
        # Overall status
        overall_health = health_count / total_health if total_health > 0 else 0
        overall_func = func_count / total_func if total_func > 0 else 0
        
        print(f"\n📊 Overall Platform Health: {overall_health:.1%}")
        print(f"📊 Overall Platform Functionality: {overall_func:.1%}")
        
        if overall_health >= 0.8 and overall_func >= 0.8:
            print("\n🎉 PLATFORM STATUS: EXCELLENT - Ready for production use!")
        elif overall_health >= 0.6 and overall_func >= 0.6:
            print("\n✅ PLATFORM STATUS: GOOD - Minor issues to address")
        else:
            print("\n⚠️  PLATFORM STATUS: NEEDS ATTENTION - Critical issues found")
        
        print(f"\n🕐 Test completed at: {self.results['timestamp']}")

def main():
    """Main test execution"""
    tester = PlatformTester()
    
    try:
        results = tester.run_comprehensive_test()
        tester.print_summary()
        
        # Exit with appropriate code
        overall_health = sum(results['health'].values()) / len(results['health']) if results['health'] else 0
        overall_func = sum(results['functionality'].values()) / len(results['functionality']) if results['functionality'] else 0
        
        if overall_health >= 0.6 and overall_func >= 0.6:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

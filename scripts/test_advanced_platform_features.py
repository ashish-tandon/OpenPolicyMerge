#!/usr/bin/env python3
"""
OpenPolicy Platform Advanced Features Test Script

This script tests the advanced functionality including:
- Enhanced ETL capabilities
- Advanced search features
- Advanced notification features
- Service analytics and metrics
- Platform integration
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

class AdvancedPlatformTester:
    def __init__(self):
        self.base_urls = {
            'etl': 'http://localhost:8007',
            'search': 'http://localhost:9002',
            'notification': 'http://localhost:9004',
            'auth': 'http://localhost:9003',
            'config': 'http://localhost:9005',
            'error_reporting': 'http://localhost:9024'
        }
        self.results = {}
        
    def test_enhanced_etl_features(self) -> Dict[str, bool]:
        """Test enhanced ETL service functionality"""
        results = {}
        
        try:
            # Test analytics endpoint
            response = requests.get(f"{self.base_urls['etl']}/analytics/summary", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ETL Analytics: {data['total_jobs']} total jobs, {data['success_rate']:.1%} success rate")
                results['analytics'] = True
            else:
                print(f"❌ ETL Analytics: Failed (Status: {response.status_code})")
                results['analytics'] = False
        except Exception as e:
            print(f"❌ ETL Analytics: Error - {str(e)}")
            results['analytics'] = False
        
        try:
            # Test pipeline execution
            response = requests.post(f"{self.base_urls['etl']}/pipelines/policy-data/execute", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ETL Pipeline Execution: {data['pipeline_id']} started successfully")
                results['pipeline_execution'] = True
            else:
                print(f"❌ ETL Pipeline Execution: Failed (Status: {response.status_code})")
                results['pipeline_execution'] = False
        except Exception as e:
            print(f"❌ ETL Pipeline Execution: Error - {str(e)}")
            results['pipeline_execution'] = False
        
        try:
            # Test pipeline status
            response = requests.get(f"{self.base_urls['etl']}/pipelines/policy-data/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ETL Pipeline Status: {data['pipeline_id']} is {data['status']}")
                results['pipeline_status'] = True
            else:
                print(f"❌ ETL Pipeline Status: Failed (Status: {response.status_code})")
                results['pipeline_status'] = False
        except Exception as e:
            print(f"❌ ETL Pipeline Status: Error - {str(e)}")
            results['pipeline_status'] = False
        
        return results
    
    def test_enhanced_search_features(self) -> Dict[str, bool]:
        """Test enhanced search service functionality"""
        results = {}
        
        try:
            # Test advanced search
            response = requests.get(f"{self.base_urls['search']}/search/advanced?query=policy&limit=3", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Advanced Search: {data['total_results']} results for 'policy' query")
                results['advanced_search'] = True
            else:
                print(f"❌ Advanced Search: Failed (Status: {response.status_code})")
                results['advanced_search'] = False
        except Exception as e:
            print(f"❌ Advanced Search: Error - {str(e)}")
            results['advanced_search'] = False
        
        try:
            # Test search suggestions
            response = requests.get(f"{self.base_urls['search']}/search/suggestions?query=pol", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Search Suggestions: {len(data['suggestions'])} suggestions for 'pol'")
                results['search_suggestions'] = True
            else:
                print(f"❌ Search Suggestions: Failed (Status: {response.status_code})")
                results['search_suggestions'] = False
        except Exception as e:
            print(f"❌ Search Suggestions: Error - {str(e)}")
            results['search_suggestions'] = False
        
        try:
            # Test trending searches
            response = requests.get(f"{self.base_urls['search']}/search/trending", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Trending Searches: {len(data['trending'])} trending queries")
                results['trending_searches'] = True
            else:
                print(f"❌ Trending Searches: Failed (Status: {response.status_code})")
                results['trending_searches'] = False
        except Exception as e:
            print(f"❌ Trending Searches: Error - {str(e)}")
            results['trending_searches'] = False
        
        return results
    
    def test_enhanced_notification_features(self) -> Dict[str, bool]:
        """Test enhanced notification service functionality"""
        results = {}
        
        try:
            # Test notification statistics
            response = requests.get(f"{self.base_urls['notification']}/notifications/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Notification Stats: {data['total_notifications_sent']} total, {data['delivery_success_rate']:.1%} success rate")
                results['notification_stats'] = True
            else:
                print(f"❌ Notification Stats: Failed (Status: {response.status_code})")
                results['notification_stats'] = False
        except Exception as e:
            print(f"❌ Notification Stats: Error - {str(e)}")
            results['notification_stats'] = False
        
        try:
            # Test user notifications
            response = requests.get(f"{self.base_urls['notification']}/notifications/user/test-user-123?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User Notifications: {data['total_notifications']} total, {data['unread_count']} unread")
                results['user_notifications'] = True
            else:
                print(f"❌ User Notifications: Failed (Status: {response.status_code})")
                results['user_notifications'] = False
        except Exception as e:
            print(f"❌ User Notifications: Error - {str(e)}")
            results['user_notifications'] = False
        
        try:
            # Test bulk notifications
            bulk_data = [
                {"user_id": "user1", "message": "Bulk test 1", "type": "info"},
                {"user_id": "user2", "message": "Bulk test 2", "type": "info"}
            ]
            response = requests.post(f"{self.base_urls['notification']}/notifications/bulk", json=bulk_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Bulk Notifications: {data['total_sent']} notifications sent successfully")
                results['bulk_notifications'] = True
            else:
                print(f"❌ Bulk Notifications: Failed (Status: {response.status_code})")
                results['bulk_notifications'] = False
        except Exception as e:
            print(f"❌ Bulk Notifications: Error - {str(e)}")
            results['bulk_notifications'] = False
        
        return results
    
    def test_service_integration(self) -> Dict[str, bool]:
        """Test service integration and communication"""
        results = {}
        
        try:
            # Test ETL job creation (basic functionality)
            job_data = {
                "name": "integration-test-job",
                "type": "extract",
                "source": "test-data",
                "destination": "test-output"
            }
            response = requests.post(f"{self.base_urls['etl']}/jobs", json=job_data, timeout=10)
            if response.status_code == 201:
                print(f"✅ Service Integration: ETL job creation working")
                results['etl_integration'] = True
            else:
                print(f"❌ Service Integration: ETL job creation failed")
                results['etl_integration'] = False
        except Exception as e:
            print(f"❌ Service Integration: ETL error - {str(e)}")
            results['etl_integration'] = False
        
        try:
            # Test search integration
            response = requests.get(f"{self.base_urls['search']}/search?query=integration", timeout=10)
            if response.status_code == 200:
                print(f"✅ Service Integration: Search service working")
                results['search_integration'] = True
            else:
                print(f"❌ Service Integration: Search service failed")
                results['search_integration'] = False
        except Exception as e:
            print(f"❌ Service Integration: Search error - {str(e)}")
            results['search_integration'] = False
        
        try:
            # Test notification integration
            notif_data = {"user_id": "test-user", "message": "Integration test", "type": "info"}
            response = requests.post(f"{self.base_urls['notification']}/notifications/send", json=notif_data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Service Integration: Notification service working")
                results['notification_integration'] = True
            else:
                print(f"❌ Service Integration: Notification service failed")
                results['notification_integration'] = False
        except Exception as e:
            print(f"❌ Service Integration: Notification error - {str(e)}")
            results['notification_integration'] = False
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive advanced platform testing"""
        print("🚀 Starting OpenPolicy Platform Advanced Features Testing")
        print("=" * 70)
        
        # Test enhanced ETL features
        print("\n🔧 Testing Enhanced ETL Features:")
        print("-" * 40)
        etl_results = self.test_enhanced_etl_features()
        
        # Test enhanced search features
        print("\n🔍 Testing Enhanced Search Features:")
        print("-" * 40)
        search_results = self.test_enhanced_search_features()
        
        # Test enhanced notification features
        print("\n📢 Testing Enhanced Notification Features:")
        print("-" * 40)
        notification_results = self.test_enhanced_notification_features()
        
        # Test service integration
        print("\n🔗 Testing Service Integration:")
        print("-" * 40)
        integration_results = self.test_service_integration()
        
        # Compile results
        self.results = {
            'etl_features': etl_results,
            'search_features': search_results,
            'notification_features': notification_results,
            'integration': integration_results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.results
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 70)
        print("📋 ADVANCED PLATFORM FEATURES TEST SUMMARY")
        print("=" * 70)
        
        # ETL features summary
        etl_count = sum(self.results['etl_features'].values())
        total_etl = len(self.results['etl_features'])
        print(f"\n🔧 ETL Features: {etl_count}/{total_etl} working")
        
        # Search features summary
        search_count = sum(self.results['search_features'].values())
        total_search = len(self.results['search_features'])
        print(f"🔍 Search Features: {search_count}/{total_search} working")
        
        # Notification features summary
        notif_count = sum(self.results['notification_features'].values())
        total_notif = len(self.results['notification_features'])
        print(f"📢 Notification Features: {notif_count}/{total_notif} working")
        
        # Integration summary
        integration_count = sum(self.results['integration'].values())
        total_integration = len(self.results['integration'])
        print(f"🔗 Service Integration: {integration_count}/{total_integration} working")
        
        # Overall status
        total_features = total_etl + total_search + total_notif + total_integration
        working_features = etl_count + search_count + notif_count + integration_count
        overall_score = working_features / total_features if total_features > 0 else 0
        
        print(f"\n📊 Overall Advanced Features Score: {overall_score:.1%}")
        print(f"📊 Working Features: {working_features}/{total_features}")
        
        if overall_score >= 0.9:
            print("\n🎉 PLATFORM STATUS: EXCELLENT - Advanced features fully operational!")
        elif overall_score >= 0.7:
            print("\n✅ PLATFORM STATUS: VERY GOOD - Most advanced features working")
        elif overall_score >= 0.5:
            print("\n🟡 PLATFORM STATUS: GOOD - Basic advanced features working")
        else:
            print("\n⚠️  PLATFORM STATUS: NEEDS ATTENTION - Advanced features have issues")
        
        print(f"\n🕐 Test completed at: {self.results['timestamp']}")

def main():
    """Main test execution"""
    tester = AdvancedPlatformTester()
    
    try:
        results = tester.run_comprehensive_test()
        tester.print_summary()
        
        # Exit with appropriate code
        total_features = len(results['etl_features']) + len(results['search_features']) + len(results['notification_features']) + len(results['integration'])
        working_features = sum(results['etl_features'].values()) + sum(results['search_features'].values()) + sum(results['notification_features'].values()) + sum(results['integration'].values())
        overall_score = working_features / total_features if total_features > 0 else 0
        
        if overall_score >= 0.7:
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

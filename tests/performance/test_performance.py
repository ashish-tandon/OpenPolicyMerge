"""
Performance Testing Suite for OpenPolicy Platform
Tests system performance, scalability, and resource usage under load.
"""

import asyncio
import time
import statistics
import psutil
import httpx
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import json
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance test metrics."""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    average_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    timestamp: datetime

class PerformanceTester:
    """Performance testing framework for OpenPolicy Platform."""
    
    def __init__(self, base_urls: Dict[str, str]):
        self.base_urls = base_urls
        self.client = httpx.AsyncClient(timeout=60.0)
        self.metrics: List[PerformanceMetrics] = []
        
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3)
        }
    
    async def single_request_test(self, url: str, method: str = 'GET', 
                                data: Dict = None, headers: Dict = None) -> Tuple[float, int, str]:
        """Execute a single HTTP request and measure response time."""
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = await self.client.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = await self.client.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = await self.client.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            return response_time, response.status_code, "success"
            
        except Exception as e:
            response_time = time.time() - start_time
            return response_time, 0, str(e)
    
    async def load_test(self, test_name: str, url: str, method: str = 'GET',
                       data: Dict = None, headers: Dict = None,
                       concurrent_users: int = 10, total_requests: int = 100) -> PerformanceMetrics:
        """Execute a load test with specified concurrency and request count."""
        logger.info(f"Starting load test: {test_name}")
        logger.info(f"URL: {url}, Method: {method}, Concurrent Users: {concurrent_users}, Total Requests: {total_requests}")
        
        # Get initial system metrics
        initial_metrics = self.get_system_metrics()
        logger.info(f"Initial system metrics: {initial_metrics}")
        
        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_users)
        
        async def make_request():
            async with semaphore:
                response_time, status_code, result = await self.single_request_test(url, method, data, headers)
                response_times.append(response_time)
                
                if result == "success" and 200 <= status_code < 400:
                    nonlocal successful_requests
                    successful_requests += 1
                else:
                    nonlocal failed_requests
                    failed_requests += 1
                
                return response_time, status_code, result
        
        # Execute requests
        tasks = [make_request() for _ in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
        
        requests_per_second = total_requests / total_time if total_time > 0 else 0
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        # Get final system metrics
        final_metrics = self.get_system_metrics()
        logger.info(f"Final system metrics: {final_metrics}")
        
        # Create metrics object
        metrics = PerformanceMetrics(
            test_name=test_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            timestamp=datetime.now()
        )
        
        self.metrics.append(metrics)
        
        # Log results
        logger.info(f"Load test completed: {test_name}")
        logger.info(f"Success Rate: {(successful_requests/total_requests)*100:.2f}%")
        logger.info(f"Average Response Time: {avg_response_time:.3f}s")
        logger.info(f"Requests per Second: {requests_per_second:.2f}")
        
        return metrics
    
    async def stress_test(self, test_name: str, url: str, method: str = 'GET',
                         data: Dict = None, headers: Dict = None,
                         max_concurrent_users: int = 100, step_size: int = 10) -> List[PerformanceMetrics]:
        """Execute a stress test to find the breaking point."""
        logger.info(f"Starting stress test: {test_name}")
        
        stress_metrics = []
        current_concurrent = step_size
        
        while current_concurrent <= max_concurrent_users:
            logger.info(f"Testing with {current_concurrent} concurrent users...")
            
            metrics = await self.load_test(
                test_name=f"{test_name}_{current_concurrent}_users",
                url=url,
                method=method,
                data=data,
                headers=headers,
                concurrent_users=current_concurrent,
                total_requests=current_concurrent * 2  # 2 requests per user
            )
            
            stress_metrics.append(metrics)
            
            # Check if we've hit the breaking point
            if metrics.error_rate > 0.1:  # More than 10% errors
                logger.warning(f"Breaking point reached at {current_concurrent} concurrent users")
                break
            
            if metrics.average_response_time > 5.0:  # More than 5 seconds
                logger.warning(f"Response time threshold exceeded at {current_concurrent} concurrent users")
                break
            
            current_concurrent += step_size
        
        return stress_metrics
    
    async def endurance_test(self, test_name: str, url: str, method: str = 'GET',
                           data: Dict = None, headers: Dict = None,
                           concurrent_users: int = 20, duration_minutes: int = 30) -> PerformanceMetrics:
        """Execute an endurance test to check system stability over time."""
        logger.info(f"Starting endurance test: {test_name}")
        logger.info(f"Duration: {duration_minutes} minutes, Concurrent Users: {concurrent_users}")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_users)
        
        async def make_request():
            async with semaphore:
                response_time, status_code, result = await self.single_request_test(url, method, data, headers)
                response_times.append(response_time)
                
                if result == "success" and 200 <= status_code < 400:
                    nonlocal successful_requests
                    successful_requests += 1
                else:
                    nonlocal failed_requests
                    failed_requests += 1
                
                return response_time, status_code, result
        
        # Continuous request loop
        while time.time() < end_time:
            # Create batch of requests
            batch_size = min(concurrent_users, 50)  # Limit batch size
            tasks = [make_request() for _ in range(batch_size)]
            
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"Batch execution error: {e}")
            
            # Small delay between batches
            await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        # Calculate metrics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
        
        requests_per_second = total_requests / total_time if total_time > 0 else 0
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            test_name=test_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            timestamp=datetime.now()
        )
        
        self.metrics.append(metrics)
        
        logger.info(f"Endurance test completed: {test_name}")
        logger.info(f"Total Requests: {total_requests}, Success Rate: {(successful_requests/total_requests)*100:.2f}%")
        
        return metrics
    
    def generate_report(self) -> str:
        """Generate a comprehensive performance test report."""
        if not self.metrics:
            return "No performance metrics available."
        
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(self.metrics)}")
        report.append("")
        
        # Summary statistics
        total_requests = sum(m.total_requests for m in self.metrics)
        total_successful = sum(m.successful_requests for m in self.metrics)
        total_failed = sum(m.failed_requests for m in self.metrics)
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Requests: {total_requests:,}")
        report.append(f"Successful: {total_successful:,}")
        report.append(f"Failed: {total_failed:,}")
        report.append(f"Overall Success Rate: {overall_success_rate:.2f}%")
        report.append("")
        
        # Individual test results
        report.append("INDIVIDUAL TEST RESULTS")
        report.append("-" * 40)
        
        for metric in self.metrics:
            report.append(f"Test: {metric.test_name}")
            report.append(f"  Requests: {metric.total_requests:,} | Success: {metric.successful_requests:,} | Failed: {metric.failed_requests:,}")
            report.append(f"  Success Rate: {(metric.successful_requests/metric.total_requests)*100:.2f}%")
            report.append(f"  Avg Response Time: {metric.average_response_time:.3f}s")
            report.append(f"  P95 Response Time: {metric.p95_response_time:.3f}s")
            report.append(f"  Requests/sec: {metric.requests_per_second:.2f}")
            report.append("")
        
        # Performance recommendations
        report.append("PERFORMANCE RECOMMENDATIONS")
        report.append("-" * 40)
        
        # Analyze response times
        avg_response_times = [m.average_response_time for m in self.metrics if m.average_response_time > 0]
        if avg_response_times:
            avg_avg = statistics.mean(avg_response_times)
            if avg_avg > 2.0:
                report.append("⚠️  Average response times are high (>2s). Consider:")
                report.append("   - Database query optimization")
                report.append("   - Caching implementation")
                report.append("   - Service scaling")
            elif avg_avg > 1.0:
                report.append("⚠️  Response times are moderate (>1s). Consider:")
                report.append("   - Performance monitoring")
                report.append("   - Load testing at higher concurrency")
        
        # Analyze error rates
        high_error_rates = [m for m in self.metrics if m.error_rate > 0.05]
        if high_error_rates:
            report.append("🚨 High error rates detected. Consider:")
            report.append("   - Error handling improvements")
            report.append("   - Service health monitoring")
            report.append("   - Circuit breaker implementation")
        
        # Analyze throughput
        low_throughput = [m for m in self.metrics if m.requests_per_second < 10]
        if low_throughput:
            report.append("🐌 Low throughput detected. Consider:")
            report.append("   - Service optimization")
            report.append("   - Resource scaling")
            report.append("   - Load balancing")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_metrics(self, filename: str = None):
        """Save performance metrics to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
        
        # Convert metrics to serializable format
        serializable_metrics = []
        for metric in self.metrics:
            serializable_metrics.append({
                'test_name': metric.test_name,
                'total_requests': metric.total_requests,
                'successful_requests': metric.successful_requests,
                'failed_requests': metric.failed_requests,
                'total_time': metric.total_time,
                'average_response_time': metric.average_response_time,
                'min_response_time': metric.min_response_time,
                'max_response_time': metric.max_response_time,
                'p95_response_time': metric.p95_response_time,
                'p99_response_time': metric.p99_response_time,
                'requests_per_second': metric.requests_per_second,
                'error_rate': metric.error_rate,
                'timestamp': metric.timestamp.isoformat()
            })
        
        with open(filename, 'w') as f:
            json.dump(serializable_metrics, f, indent=2)
        
        logger.info(f"Performance metrics saved to: {filename}")

async def run_performance_tests():
    """Run a comprehensive performance test suite."""
    # Test configuration
    base_urls = {
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
    
    tester = PerformanceTester(base_urls)
    
    try:
        logger.info("🚀 Starting Performance Test Suite...")
        
        # Test data for POST requests
        test_policy = {
            'name': 'Performance Test Policy',
            'description': 'Policy for performance testing',
            'content': 'package test.policy\n\ndefault allow = false\n\nallow { input.user.role == "admin" }',
            'version': '1.0.0'
        }
        
        test_search_doc = {
            'document_type': 'policy',
            'document_id': 'perf-test-001',
            'title': 'Performance Test Document',
            'content': 'This is a test document for performance testing.'
        }
        
        # 1. Load Tests
        logger.info("\n📊 Running Load Tests...")
        
        # API Gateway load test
        await tester.load_test(
            test_name="API Gateway Load Test",
            url=f"{base_urls['api_gateway']}/healthz",
            concurrent_users=20,
            total_requests=200
        )
        
        # Policy Service load test
        await tester.load_test(
            test_name="Policy Service Load Test",
            url=f"{base_urls['policy_service']}/healthz",
            concurrent_users=15,
            total_requests=150
        )
        
        # Search Service load test
        await tester.load_test(
            test_name="Search Service Load Test",
            url=f"{base_urls['search_service']}/healthz",
            concurrent_users=15,
            total_requests=150
        )
        
        # 2. Stress Tests
        logger.info("\n🔥 Running Stress Tests...")
        
        # API Gateway stress test
        await tester.stress_test(
            test_name="API Gateway Stress Test",
            url=f"{base_urls['api_gateway']}/healthz",
            max_concurrent_users=50,
            step_size=5
        )
        
        # 3. Endurance Tests
        logger.info("\n⏰ Running Endurance Tests...")
        
        # Health Service endurance test (shorter duration for demo)
        await tester.endurance_test(
            test_name="Health Service Endurance Test",
            url=f"{base_urls['health_service']}/healthz",
            concurrent_users=10,
            duration_minutes=2  # Short duration for demo
        )
        
        # Generate and display report
        logger.info("\n📋 Generating Performance Report...")
        report = tester.generate_report()
        print(report)
        
        # Save metrics
        tester.save_metrics()
        
        logger.info("🎉 Performance Test Suite completed!")
        
    except Exception as e:
        logger.error(f"Performance test suite failed: {e}")
        raise
    finally:
        await tester.close()

if __name__ == "__main__":
    # Run the performance test suite
    asyncio.run(run_performance_tests())

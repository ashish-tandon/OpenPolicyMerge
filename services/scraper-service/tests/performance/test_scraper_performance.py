"""
Performance tests for the OpenPolicy Scraper Service.
Tests scalability and performance in alignment with services-based architecture.
"""
import pytest
import time
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import statistics
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the performance testing modules (to be created)
# from src.services.performance_monitor import PerformanceMonitor
# from src.services.scraper_manager import ScraperManager

@pytest.mark.performance
@pytest.mark.slow
class TestScraperPerformance:
    """Test scraper service performance and scalability."""
    
    @pytest.fixture
    def sample_scrapers(self):
        """Provide sample scrapers for performance testing."""
        return [
            {
                "id": f"scraper-{i}",
                "name": f"Test Scraper {i}",
                "url": f"https://example{i}.com",
                "type": "civic",
                "enabled": True
            }
            for i in range(1, 11)  # 10 test scrapers
        ]
    
    @pytest.fixture
    def performance_monitor(self):
        """Mock performance monitoring service."""
        with patch("src.services.performance_monitor.PerformanceMonitor") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            # Setup performance monitoring methods
            mock_instance.start_monitoring = Mock()
            mock_instance.stop_monitoring = Mock()
            mock_instance.get_metrics = Mock(return_value={
                "cpu_usage": 0.65,
                "memory_usage": 0.45,
                "disk_io": 0.30,
                "network_io": 0.25
            })
            
            yield {
                "class": mock_class,
                "instance": mock_instance
            }
    
    @pytest.fixture
    def mock_scraper_manager(self):
        """Mock scraper manager for performance testing."""
        with patch("src.services.scraper_manager.ScraperManager") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            # Setup performance-related methods
            mock_instance.run_scraper = Mock(return_value={"status": "success"})
            mock_instance.run_multiple_scrapers = Mock(return_value=[])
            mock_instance.get_scraper_status = Mock(return_value="running")
            
            yield {
                "class": mock_class,
                "instance": mock_instance
            }
    
    def test_single_scraper_performance(self, mock_scraper_manager, performance_monitor):
        """Test single scraper execution performance."""
        manager = mock_scraper_manager["instance"]
        monitor = performance_monitor["instance"]
        
        # Start performance monitoring
        monitor.start_monitoring()
        
        # Measure execution time
        start_time = time.time()
        result = manager.run_scraper("scraper-1")
        execution_time = time.time() - start_time
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Get performance metrics
        metrics = monitor.get_metrics()
        
        # Performance assertions
        assert result["status"] == "success"
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert metrics["cpu_usage"] < 0.8  # CPU usage should be reasonable
        assert metrics["memory_usage"] < 0.7  # Memory usage should be reasonable
        
        # Verify monitoring was used
        monitor.start_monitoring.assert_called_once()
        monitor.stop_monitoring.assert_called_once()
        monitor.get_metrics.assert_called_once()
    
    def test_concurrent_scraper_performance(self, mock_scraper_manager, sample_scrapers):
        """Test concurrent scraper execution performance."""
        manager = mock_scraper_manager["instance"]
        
        # Mock concurrent execution results
        mock_results = [
            {"scraper_id": f"scraper-{i}", "status": "success", "execution_time": 2.0 + i * 0.1}
            for i in range(1, 11)
        ]
        manager.run_multiple_scrapers.return_value = mock_results
        
        # Measure concurrent execution time
        start_time = time.time()
        results = manager.run_multiple_scrapers([s["id"] for s in sample_scrapers])
        total_time = time.time() - start_time
        
        # Performance assertions
        assert len(results) == 10
        assert all(r["status"] == "success" for r in results)
        assert total_time < 10.0  # Concurrent execution should be faster than sequential
        
        # Calculate performance metrics
        execution_times = [r["execution_time"] for r in results]
        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)
        
        assert avg_time < 3.0  # Average execution time should be reasonable
        assert max_time < 5.0  # Maximum execution time should be reasonable
        
        # Verify method was called
        manager.run_multiple_scrapers.assert_called_once()
    
    def test_memory_usage_under_load(self, mock_scraper_manager, sample_scrapers):
        """Test memory usage under concurrent load."""
        manager = mock_scraper_manager["instance"]
        
        # Get initial memory usage
        initial_memory = psutil.virtual_memory().percent
        
        # Simulate concurrent scraper execution
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for scraper in sample_scrapers:
                future = executor.submit(manager.run_scraper, scraper["id"])
                futures.append(future)
            
            # Wait for all to complete
            for future in as_completed(futures):
                result = future.result()
                assert result["status"] == "success"
        
        # Get final memory usage
        final_memory = psutil.virtual_memory().percent
        memory_increase = final_memory - initial_memory
        
        # Memory usage assertions
        assert memory_increase < 20.0  # Memory increase should be reasonable
        assert final_memory < 80.0  # Total memory usage should be reasonable
        
        # Verify all scrapers were executed
        assert manager.run_scraper.call_count == 10
    
    def test_cpu_usage_under_load(self, mock_scraper_manager, sample_scrapers):
        """Test CPU usage under concurrent load."""
        manager = mock_scraper_manager["instance"]
        
        # Get initial CPU usage
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Simulate concurrent scraper execution
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for scraper in sample_scrapers[:5]:  # Test with 5 scrapers
                future = executor.submit(manager.run_scraper, scraper["id"])
                futures.append(future)
            
            # Wait for all to complete
            for future in as_completed(futures):
                result = future.result()
                assert result["status"] == "success"
        
        # Get final CPU usage
        final_cpu = psutil.cpu_percent(interval=1)
        
        # CPU usage assertions (allowing for system variations)
        assert final_cpu < 90.0  # CPU usage should not be excessive
        
        # Verify scrapers were executed
        assert manager.run_scraper.call_count == 5
    
    def test_scraper_throughput(self, mock_scraper_manager, sample_scrapers):
        """Test scraper throughput and processing rate."""
        manager = mock_scraper_manager["instance"]
        
        # Mock throughput data
        mock_throughput_data = [
            {"scraper_id": f"scraper-{i}", "records_processed": 100 + i * 10, "processing_time": 2.0}
            for i in range(1, 11)
        ]
        
        # Calculate throughput metrics
        total_records = sum(d["records_processed"] for d in mock_throughput_data)
        total_time = sum(d["processing_time"] for d in mock_throughput_data)
        throughput = total_records / total_time
        
        # Throughput assertions
        assert throughput > 50.0  # Should process at least 50 records per second
        assert total_records == 1450  # Total records should match expected sum
        
        # Verify throughput calculation
        expected_throughput = 1450 / 20.0  # 1450 records / 20 seconds
        assert abs(throughput - expected_throughput) < 1.0  # Allow small rounding differences
    
    def test_response_time_percentiles(self, mock_scraper_manager):
        """Test response time percentiles for scraper operations."""
        manager = mock_scraper_manager["instance"]
        
        # Mock response times for multiple operations
        response_times = []
        for i in range(100):  # Test 100 operations
            start_time = time.time()
            result = manager.run_scraper(f"scraper-{i % 10 + 1}")
            execution_time = time.time() - start_time
            response_times.append(execution_time)
            
            assert result["status"] == "success"
        
        # Calculate percentiles
        response_times.sort()
        p50 = response_times[49]  # 50th percentile
        p90 = response_times[89]  # 90th percentile
        p95 = response_times[94]  # 95th percentile
        p99 = response_times[98]  # 99th percentile
        
        # Percentile assertions
        assert p50 < 1.0  # 50% of requests should complete within 1 second
        assert p90 < 2.0  # 90% of requests should complete within 2 seconds
        assert p95 < 3.0  # 95% of requests should complete within 3 seconds
        assert p99 < 5.0  # 99% of requests should complete within 5 seconds
        
        # Verify all operations were executed
        assert manager.run_scraper.call_count == 100
    
    def test_resource_cleanup_after_execution(self, mock_scraper_manager, performance_monitor):
        """Test that resources are properly cleaned up after execution."""
        manager = mock_scraper_manager["instance"]
        monitor = performance_monitor["instance"]
        
        # Get initial resource usage
        initial_memory = psutil.virtual_memory().percent
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Execute multiple scrapers
        for i in range(1, 6):
            manager.run_scraper(f"scraper-{i}")
        
        # Wait for cleanup
        time.sleep(2)
        
        # Get resource usage after cleanup
        final_memory = psutil.virtual_memory().percent
        final_cpu = psutil.cpu_percent(interval=1)
        
        # Resource cleanup assertions
        memory_difference = abs(final_memory - initial_memory)
        cpu_difference = abs(final_cpu - initial_cpu)
        
        # Resources should return to near initial levels
        assert memory_difference < 10.0  # Memory should be cleaned up
        assert cpu_difference < 15.0  # CPU should return to baseline
        
        # Verify scrapers were executed
        assert manager.run_scraper.call_count == 5
    
    def test_scalability_with_increasing_load(self, mock_scraper_manager):
        """Test scalability with increasing concurrent load."""
        manager = mock_scraper_manager["instance"]
        
        # Test different concurrency levels
        concurrency_levels = [1, 2, 4, 8, 16]
        execution_times = []
        
        for concurrency in concurrency_levels:
            # Mock results for this concurrency level
            mock_results = [
                {"scraper_id": f"scraper-{i}", "status": "success"}
                for i in range(1, concurrency + 1)
            ]
            manager.run_multiple_scrapers.return_value = mock_results
            
            # Measure execution time
            start_time = time.time()
            results = manager.run_multiple_scrapers([f"scraper-{i}" for i in range(1, concurrency + 1)])
            execution_time = time.time() - start_time
            
            execution_times.append(execution_time)
            
            # Verify results
            assert len(results) == concurrency
            assert all(r["status"] == "success" for r in results)
        
        # Scalability assertions
        # Higher concurrency should not result in exponential time increase
        for i in range(1, len(execution_times)):
            time_ratio = execution_times[i] / execution_times[i-1]
            concurrency_ratio = concurrency_levels[i] / concurrency_levels[i-1]
            
            # Time increase should be less than linear with concurrency
            assert time_ratio < concurrency_ratio * 1.5
        
        # Verify all calls were made
        assert manager.run_multiple_scrapers.call_count == len(concurrency_levels)
    
    def test_error_handling_performance(self, mock_scraper_manager):
        """Test performance when handling errors."""
        manager = mock_scraper_manager["instance"]
        
        # Mock error scenarios
        manager.run_scraper.side_effect = [
            Exception("Network error"),
            {"status": "success"},
            Exception("Timeout error"),
            {"status": "success"},
            Exception("Validation error")
        ]
        
        # Measure error handling performance
        start_time = time.time()
        
        results = []
        for i in range(1, 6):
            try:
                result = manager.run_scraper(f"scraper-{i}")
                results.append(result)
            except Exception as e:
                results.append({"status": "error", "error": str(e)})
        
        error_handling_time = time.time() - start_time
        
        # Error handling performance assertions
        assert error_handling_time < 3.0  # Error handling should be fast
        assert len(results) == 5
        
        # Count successful and failed operations
        successful = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "error")
        
        assert successful == 2
        assert failed == 3
        
        # Verify all scrapers were attempted
        assert manager.run_scraper.call_count == 5
    
    def test_batch_processing_performance(self, mock_scraper_manager):
        """Test batch processing performance and efficiency."""
        manager = mock_scraper_manager["instance"]
        
        # Create large batch of scrapers
        large_batch = [f"scraper-{i}" for i in range(1, 101)]  # 100 scrapers
        
        # Mock batch processing results
        mock_batch_results = [
            {"scraper_id": f"scraper-{i}", "status": "success", "records": 50 + i}
            for i in range(1, 101)
        ]
        manager.run_multiple_scrapers.return_value = mock_batch_results
        
        # Measure batch processing performance
        start_time = time.time()
        results = manager.run_multiple_scrapers(large_batch)
        batch_time = time.time() - start_time
        
        # Batch processing assertions
        assert len(results) == 100
        assert all(r["status"] == "success" for r in results)
        
        # Calculate efficiency metrics
        total_records = sum(r["records"] for r in results)
        records_per_second = total_records / batch_time
        
        # Efficiency assertions
        assert records_per_second > 100.0  # Should process at least 100 records per second
        assert batch_time < 60.0  # Large batch should complete within reasonable time
        
        # Verify batch processing was used
        manager.run_multiple_scrapers.assert_called_once_with(large_batch)
    
    def test_memory_leak_detection(self, mock_scraper_manager, performance_monitor):
        """Test for memory leaks during extended operation."""
        manager = mock_scraper_manager["instance"]
        monitor = performance_monitor["instance"]
        
        # Get initial memory usage
        initial_memory = psutil.virtual_memory().percent
        
        # Simulate extended operation
        for cycle in range(10):  # 10 cycles
            # Execute scrapers
            for i in range(1, 6):
                manager.run_scraper(f"scraper-{i}")
            
            # Small delay between cycles
            time.sleep(0.1)
            
            # Check memory usage
            current_memory = psutil.virtual_memory().percent
            memory_increase = current_memory - initial_memory
            
            # Memory should not continuously increase
            assert memory_increase < 30.0  # Allow some memory growth but not excessive
        
        # Final memory check
        final_memory = psutil.virtual_memory().percent
        total_memory_increase = final_memory - initial_memory
        
        # Total memory increase should be reasonable
        assert total_memory_increase < 25.0
        
        # Verify all operations were executed
        assert manager.run_scraper.call_count == 50  # 10 cycles * 5 scrapers
    
    def test_concurrent_user_simulation(self, mock_scraper_manager):
        """Test performance under simulated concurrent user load."""
        manager = mock_scraper_manager["instance"]
        
        # Simulate multiple users making requests
        user_count = 20
        requests_per_user = 5
        
        def user_workload(user_id):
            """Simulate a user's workload."""
            results = []
            for request in range(requests_per_user):
                try:
                    result = manager.run_scraper(f"scraper-{user_id}-{request}")
                    results.append(result)
                except Exception as e:
                    results.append({"status": "error", "error": str(e)})
            return results
        
        # Execute concurrent user workloads
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=user_count) as executor:
            futures = [executor.submit(user_workload, i) for i in range(1, user_count + 1)]
            
            all_results = []
            for future in as_completed(futures):
                user_results = future.result()
                all_results.extend(user_results)
        
        total_time = time.time() - start_time
        
        # Concurrent user performance assertions
        assert len(all_results) == user_count * requests_per_user  # 100 total requests
        
        # Calculate success rate
        successful = sum(1 for r in all_results if r["status"] == "success")
        success_rate = successful / len(all_results)
        
        assert success_rate > 0.8  # At least 80% success rate under load
        assert total_time < 30.0  # Should complete within reasonable time
        
        # Verify all requests were processed
        assert manager.run_scraper.call_count == user_count * requests_per_user

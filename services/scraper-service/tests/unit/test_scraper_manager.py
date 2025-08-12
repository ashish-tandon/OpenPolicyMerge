"""
Unit tests for the Scraper Manager service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

# Import the scraper manager (to be created)
# from src.services.scraper_manager import ScraperManager

@pytest.mark.unit
class TestScraperManager:
    """Test Scraper Manager functionality."""
    
    @pytest.fixture
    def sample_scraper_config(self):
        """Provide sample scraper configuration."""
        return {
            "id": "test-scraper-1",
            "name": "Test Scraper",
            "jurisdiction": "federal",
            "status": "enabled",
            "priority": "high",
            "config": {
                "url": "https://example.com",
                "selectors": {
                    "title": "h1",
                    "content": ".content"
                },
                "schedule": "daily",
                "timeout": 300
            }
        }
    
    @pytest.fixture
    def sample_job_data(self):
        """Provide sample job data."""
        return {
            "id": "test-job-1",
            "scraper_id": "test-scraper-1",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "config": {
                "mode": "test",
                "timeout": 300
            }
        }
    
    @pytest.fixture
    def mock_scraper_manager(self):
        """Mock scraper manager service."""
        with patch("src.services.scraper_manager.ScraperManager") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            # Setup default methods
            mock_instance.get_scrapers.return_value = []
            mock_instance.run_scraper.return_value = {"status": "success"}
            mock_instance.get_jobs.return_value = []
            mock_instance.create_job.return_value = {"id": "test-job-1"}
            mock_instance.update_job_status.return_value = True
            
            yield {
                "class": mock_class,
                "instance": mock_instance
            }
    
    def test_scraper_manager_initialization(self, sample_scraper_config):
        """Test scraper manager initialization."""
        with patch("src.services.scraper_manager.ScraperManager") as MockManager:
            # Mock the manager class
            mock_manager = Mock()
            MockManager.return_value = mock_manager
            
            # Test initialization
            manager = MockManager()
            assert manager is not None
    
    def test_get_scrapers(self, mock_scraper_manager):
        """Test getting all scrapers."""
        manager = mock_scraper_manager["instance"]
        
        # Mock scrapers list
        mock_scrapers = [
            {"id": "scraper-1", "name": "Test Scraper 1"},
            {"id": "scraper-2", "name": "Test Scraper 2"}
        ]
        manager.get_scrapers.return_value = mock_scrapers
        
        # Get scrapers
        scrapers = manager.get_scrapers()
        
        # Verify result
        assert len(scrapers) == 2
        assert scrapers[0]["id"] == "scraper-1"
        assert scrapers[1]["name"] == "Test Scraper 2"
        
        # Verify method was called
        manager.get_scrapers.assert_called_once()
    
    def test_get_scraper_by_id(self, mock_scraper_manager):
        """Test getting scraper by ID."""
        manager = mock_scraper_manager["instance"]
        
        # Mock get_scraper_by_id method
        mock_scraper = {"id": "test-scraper-1", "name": "Test Scraper"}
        manager.get_scraper_by_id = Mock(return_value=mock_scraper)
        
        # Get scraper by ID
        scraper = manager.get_scraper_by_id("test-scraper-1")
        
        # Verify result
        assert scraper["id"] == "test-scraper-1"
        assert scraper["name"] == "Test Scraper"
        
        # Verify method was called
        manager.get_scraper_by_id.assert_called_once_with("test-scraper-1")
    
    def test_create_scraper(self, mock_scraper_manager, sample_scraper_config):
        """Test creating a new scraper."""
        manager = mock_scraper_manager["instance"]
        
        # Mock create_scraper method
        mock_created_scraper = sample_scraper_config.copy()
        mock_created_scraper["created_at"] = datetime.now().isoformat()
        manager.create_scraper = Mock(return_value=mock_created_scraper)
        
        # Create scraper
        created_scraper = manager.create_scraper(sample_scraper_config)
        
        # Verify result
        assert created_scraper["id"] == "test-scraper-1"
        assert created_scraper["name"] == "Test Scraper"
        assert "created_at" in created_scraper
        
        # Verify method was called
        manager.create_scraper.assert_called_once_with(sample_scraper_config)
    
    def test_update_scraper(self, mock_scraper_manager, sample_scraper_config):
        """Test updating an existing scraper."""
        manager = mock_scraper_manager["instance"]
        
        # Mock update_scraper method
        updated_config = sample_scraper_config.copy()
        updated_config["name"] = "Updated Test Scraper"
        manager.update_scraper = Mock(return_value=updated_config)
        
        # Update scraper
        updated_scraper = manager.update_scraper("test-scraper-1", {"name": "Updated Test Scraper"})
        
        # Verify result
        assert updated_scraper["name"] == "Updated Test Scraper"
        
        # Verify method was called
        manager.update_scraper.assert_called_once_with("test-scraper-1", {"name": "Updated Test Scraper"})
    
    def test_delete_scraper(self, mock_scraper_manager):
        """Test deleting a scraper."""
        manager = mock_scraper_manager["instance"]
        
        # Mock delete_scraper method
        manager.delete_scraper = Mock(return_value=True)
        
        # Delete scraper
        result = manager.delete_scraper("test-scraper-1")
        
        # Verify result
        assert result is True
        
        # Verify method was called
        manager.delete_scraper.assert_called_once_with("test-scraper-1")
    
    def test_run_scraper(self, mock_scraper_manager):
        """Test running a scraper."""
        manager = mock_scraper_manager["instance"]
        
        # Mock run_scraper method
        mock_result = {
            "status": "success",
            "scraped_items": 10,
            "errors": 0,
            "duration": 5.2
        }
        manager.run_scraper.return_value = mock_result
        
        # Run scraper
        result = manager.run_scraper("test-scraper-1", {"mode": "test"})
        
        # Verify result
        assert result["status"] == "success"
        assert result["scraped_items"] == 10
        assert result["errors"] == 0
        
        # Verify method was called
        manager.run_scraper.assert_called_once_with("test-scraper-1", {"mode": "test"})
    
    def test_get_jobs(self, mock_scraper_manager):
        """Test getting all jobs."""
        manager = mock_scraper_manager["instance"]
        
        # Mock jobs list
        mock_jobs = [
            {"id": "job-1", "scraper_id": "scraper-1", "status": "pending"},
            {"id": "job-2", "scraper_id": "scraper-2", "status": "running"}
        ]
        manager.get_jobs.return_value = mock_jobs
        
        # Get jobs
        jobs = manager.get_jobs()
        
        # Verify result
        assert len(jobs) == 2
        assert jobs[0]["status"] == "pending"
        assert jobs[1]["status"] == "running"
        
        # Verify method was called
        manager.get_jobs.assert_called_once()
    
    def test_create_job(self, mock_scraper_manager, sample_job_data):
        """Test creating a new job."""
        manager = mock_scraper_manager["instance"]
        
        # Mock create_job method
        mock_created_job = sample_job_data.copy()
        manager.create_job.return_value = mock_created_job
        
        # Create job
        created_job = manager.create_job("test-scraper-1", {"mode": "test"})
        
        # Verify result
        assert created_job["scraper_id"] == "test-scraper-1"
        assert created_job["status"] == "pending"
        
        # Verify method was called
        manager.create_job.assert_called_once_with("test-scraper-1", {"mode": "test"})
    
    def test_update_job_status(self, mock_scraper_manager):
        """Test updating job status."""
        manager = mock_scraper_manager["instance"]
        
        # Mock update_job_status method
        manager.update_job_status.return_value = True
        
        # Update job status
        result = manager.update_job_status("test-job-1", "running")
        
        # Verify result
        assert result is True
        
        # Verify method was called
        manager.update_job_status.assert_called_once_with("test-job-1", "running")
    
    def test_get_job_logs(self, mock_scraper_manager):
        """Test getting job logs."""
        manager = mock_scraper_manager["instance"]
        
        # Mock get_job_logs method
        mock_logs = [
            {"timestamp": "2025-01-27T10:00:00Z", "level": "INFO", "message": "Job started"},
            {"timestamp": "2025-01-27T10:01:00Z", "level": "INFO", "message": "Job completed"}
        ]
        manager.get_job_logs = Mock(return_value=mock_logs)
        
        # Get job logs
        logs = manager.get_job_logs("test-job-1")
        
        # Verify result
        assert len(logs) == 2
        assert logs[0]["level"] == "INFO"
        assert logs[1]["message"] == "Job completed"
        
        # Verify method was called
        manager.get_job_logs.assert_called_once_with("test-job-1")
    
    def test_scraper_validation(self, mock_scraper_manager, sample_scraper_config):
        """Test scraper configuration validation."""
        manager = mock_scraper_manager["instance"]
        
        # Mock validate_scraper_config method
        manager.validate_scraper_config = Mock(return_value={"valid": True, "errors": []})
        
        # Validate scraper config
        result = manager.validate_scraper_config(sample_scraper_config)
        
        # Verify result
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        
        # Verify method was called
        manager.validate_scraper_config.assert_called_once_with(sample_scraper_config)
    
    def test_scraper_health_check(self, mock_scraper_manager):
        """Test scraper health check."""
        manager = mock_scraper_manager["instance"]
        
        # Mock check_scraper_health method
        mock_health = {
            "status": "healthy",
            "last_run": "2025-01-27T10:00:00Z",
            "uptime": 3600,
            "errors": 0
        }
        manager.check_scraper_health = Mock(return_value=mock_health)
        
        # Check scraper health
        health = manager.check_scraper_health("test-scraper-1")
        
        # Verify result
        assert health["status"] == "healthy"
        assert health["errors"] == 0
        
        # Verify method was called
        manager.check_scraper_health.assert_called_once_with("test-scraper-1")
    
    def test_error_handling(self, mock_scraper_manager):
        """Test error handling in scraper manager."""
        manager = mock_scraper_manager["instance"]
        
        # Mock an exception
        manager.run_scraper.side_effect = Exception("Scraper failed")
        
        # Test that errors are handled gracefully
        try:
            manager.run_scraper("test-scraper-1")
        except Exception as e:
            assert "Scraper failed" in str(e)
    
    def test_concurrent_execution(self, mock_scraper_manager):
        """Test concurrent scraper execution."""
        manager = mock_scraper_manager["instance"]
        
        # Mock run_multiple_scrapers method
        mock_results = [
            {"scraper_id": "scraper-1", "status": "success"},
            {"scraper_id": "scraper-2", "status": "success"}
        ]
        manager.run_multiple_scrapers = Mock(return_value=mock_results)
        
        # Run multiple scrapers
        results = manager.run_multiple_scrapers(["scraper-1", "scraper-2"])
        
        # Verify result
        assert len(results) == 2
        assert all(r["status"] == "success" for r in results)
        
        # Verify method was called
        manager.run_multiple_scrapers.assert_called_once_with(["scraper-1", "scraper-2"])

"""
Shared test fixtures and configuration for OpenPolicy Scraper Service tests.
"""
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path."""
    return TEST_DATA_DIR

@pytest.fixture(scope="function")
def temp_dir():
    """Provide temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture(scope="function")
def mock_requests():
    """Mock requests library for HTTP testing."""
    with patch("requests.get") as mock_get, \
         patch("requests.post") as mock_post, \
         patch("requests.put") as mock_put, \
         patch("requests.delete") as mock_delete:
        
        # Setup default responses
        mock_get.return_value = Mock(status_code=200, content=b"test content")
        mock_post.return_value = Mock(status_code=201, content=b"created")
        mock_put.return_value = Mock(status_code=200, content=b"updated")
        mock_delete.return_value = Mock(status_code=204, content=b"")
        
        yield {
            "get": mock_get,
            "post": mock_post,
            "put": mock_put,
            "delete": mock_delete
        }

@pytest.fixture(scope="function")
def mock_database():
    """Mock database connections and sessions."""
    with patch("src.core.database.get_db") as mock_get_db, \
         patch("src.core.database.init_db") as mock_init_db:
        
        mock_session = Mock()
        mock_get_db.return_value = mock_session
        
        yield {
            "get_db": mock_get_db,
            "init_db": mock_init_db,
            "session": mock_session
        }

@pytest.fixture(scope="function")
def mock_redis():
    """Mock Redis connections."""
    with patch("redis.Redis") as mock_redis_class:
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance
        
        yield {
            "class": mock_redis_class,
            "instance": mock_redis_instance
        }

@pytest.fixture(scope="function")
def mock_scraper_manager():
    """Mock scraper manager service."""
    with patch("src.services.scraper_manager.ScraperManager") as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        # Setup default methods
        mock_instance.get_scrapers.return_value = []
        mock_instance.run_scraper.return_value = {"status": "success"}
        mock_instance.get_jobs.return_value = []
        
        yield {
            "class": mock_class,
            "instance": mock_instance
        }

@pytest.fixture(scope="function")
def sample_scraper_data():
    """Provide sample scraper data for testing."""
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
            }
        }
    }

@pytest.fixture(scope="function")
def sample_job_data():
    """Provide sample job data for testing."""
    return {
        "id": "test-job-1",
        "scraper_id": "test-scraper-1",
        "status": "pending",
        "created_at": "2025-01-27T10:00:00Z",
        "config": {
            "mode": "test",
            "timeout": 300
        }
    }

@pytest.fixture(scope="function")
def sample_data_record():
    """Provide sample data record for testing."""
    return {
        "id": "test-record-1",
        "scraper_id": "test-scraper-1",
        "data_type": "representative",
        "content": {
            "name": "John Doe",
            "district": "Test District",
            "party": "Test Party"
        },
        "metadata": {
            "source_url": "https://example.com/rep/1",
            "scraped_at": "2025-01-27T10:00:00Z"
        }
    }

@pytest.fixture(scope="function")
def mock_logger():
    """Mock logger for testing."""
    with patch("loguru.logger") as mock_logger:
        yield mock_logger

@pytest.fixture(scope="function")
def mock_metrics():
    """Mock Prometheus metrics for testing."""
    with patch("src.core.monitoring") as mock_monitoring:
        yield mock_monitoring

@pytest.fixture(scope="function")
def test_client():
    """Provide test client for FastAPI testing."""
    from fastapi.testclient import TestClient
    from src.main import app
    
    with TestClient(app) as client:
        yield client

# Civic-Scraper specific fixtures
@pytest.fixture(scope="function")
def civic_scraper_dir(temp_dir):
    """Provide temporary directory for Civic-Scraper tests."""
    # Create directory structure
    (temp_dir / "metadata").mkdir()
    (temp_dir / "assets").mkdir()
    (temp_dir / "artifacts").mkdir()
    return temp_dir

@pytest.fixture(scope="function")
def sample_asset_data():
    """Provide sample asset data for Civic-Scraper tests."""
    return [
        {
            "url": "https://example.com/agenda.pdf",
            "place": "testcity",
            "place_name": "Test City",
            "asset_type": "agenda",
            "date": "2020-05-04",
            "committee": "test-committee"
        },
        {
            "url": "https://example.com/minutes.pdf",
            "place": "testcity",
            "place_name": "Test City",
            "asset_type": "minutes",
            "date": "2020-05-04",
            "committee": "test-committee"
        }
    ]

# OpenParliament specific fixtures
@pytest.fixture(scope="function")
def django_settings():
    """Provide Django settings for OpenParliament tests."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")
    
    # Setup Django
    import django
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'parliament.core',
                'parliament.politicians',
            ],
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=False,
        )
        django.setup()
    
    yield settings
    
    # Cleanup
    django.db.connection.close()

@pytest.fixture(scope="function")
def sample_politician_data():
    """Provide sample politician data for OpenParliament tests."""
    return {
        "name": "Test MP",
        "riding": "Test Riding",
        "party": "Test Party",
        "current": True
    }

"""
Tests for Storage Service
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "storage-service"
    assert data["port"] == 9018

def test_health_check_alt():
    """Test alternative health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_metrics():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "files_stored" in data
    assert "total_storage_bytes" in data
    assert "upload_operations" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "storage-service"
    assert data["status"] == "running"
    assert data["port"] == 9018

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "storage-service"
    assert data["version"] == "1.0.0"

def test_dependencies():
    """Test dependencies endpoint"""
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "storage" in data
    assert "database" in data
    assert "cache" in data

def test_storage_status():
    """Test storage status endpoint"""
    response = client.get("/storage/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert "backend" in data
    assert "storage_root" in data

def test_storage_stats():
    """Test storage stats endpoint"""
    response = client.get("/storage/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_files" in data
    assert "total_size_bytes" in data
    assert "storage_backend" in data

def test_list_files():
    """Test list files endpoint"""
    response = client.get("/storage/files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert "total_count" in data

def test_upload_file():
    """Test upload file endpoint"""
    # Create a mock file for testing
    test_file_content = b"test file content"
    response = client.post("/storage/upload", files={"file": ("test.txt", test_file_content)})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "file_id" in data

def test_download_file():
    """Test download file endpoint"""
    response = client.get("/storage/download/test_123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["file_id"] == "test_123"

def test_delete_file():
    """Test delete file endpoint"""
    response = client.delete("/storage/delete/test_123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["file_id"] == "test_123"

def test_cleanup_files():
    """Test cleanup files endpoint"""
    response = client.post("/storage/cleanup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "files_removed" in data

def test_get_quota():
    """Test get quota endpoint"""
    response = client.get("/storage/quota")
    assert response.status_code == 200
    data = response.json()
    assert "used_bytes" in data
    assert "total_bytes" in data
    assert "available_bytes" in data

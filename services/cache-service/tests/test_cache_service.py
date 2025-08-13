"""
Tests for Cache Service
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
    assert data["service"] == "cache-service"
    assert data["port"] == 9016

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
    assert "cache_hits" in data
    assert "cache_misses" in data
    assert "cache_hit_rate" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "cache-service"
    assert data["status"] == "running"
    assert data["port"] == 9016

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "cache-service"
    assert data["version"] == "1.0.0"

def test_dependencies():
    """Test dependencies endpoint"""
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "redis" in data
    assert "database" in data
    assert "queue" in data

def test_cache_status():
    """Test cache status endpoint"""
    response = client.get("/cache/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert "redis_host" in data
    assert "redis_port" in data

def test_cache_stats():
    """Test cache stats endpoint"""
    response = client.get("/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_keys" in data
    assert "hit_rate" in data
    assert "ttl" in data

def test_cache_keys():
    """Test cache keys endpoint"""
    response = client.get("/cache/keys")
    assert response.status_code == 200
    data = response.json()
    assert "keys" in data
    assert "total_count" in data

def test_cache_set():
    """Test cache set endpoint"""
    response = client.post("/cache/set", json={"key": "test_key", "value": "test_value"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["key"] == "test_key"

def test_cache_get():
    """Test cache get endpoint"""
    response = client.get("/cache/get/test_key")
    assert response.status_code == 200
    data = response.json()
    assert "key" in data
    assert "found" in data

def test_cache_delete():
    """Test cache delete endpoint"""
    response = client.delete("/cache/delete/test_key")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["key"] == "test_key"

def test_cache_clear():
    """Test cache clear endpoint"""
    response = client.post("/cache/clear")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "keys_removed" in data

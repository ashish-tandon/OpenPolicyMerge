"""
Tests for Database Service
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
    assert data["service"] == "database-service"
    assert data["port"] == 9015

def test_health_alt():
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
    assert "requests_total" in data
    assert "errors_total" in data
    assert "response_time_avg" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "database-service"
    assert data["status"] == "running"

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "database-service"
    assert data["version"] == "1.0.0"

def test_dependencies():
    """Test dependencies endpoint"""
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "cache" in data
    assert "external_apis" in data

def test_database_status():
    """Test database status endpoint"""
    response = client.get("/database/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "pool_size" in data
    assert "active_connections" in data

def test_database_connections():
    """Test database connections endpoint"""
    response = client.get("/database/connections")
    assert response.status_code == 200
    data = response.json()
    assert "total_connections" in data
    assert "active_connections" in data
    assert "idle_connections" in data

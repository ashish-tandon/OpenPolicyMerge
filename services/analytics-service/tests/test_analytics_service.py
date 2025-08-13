"""
Tests for Analytics Service
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
    assert data["service"] == "analytics-service"
    assert data["port"] == 9013

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
    assert "queries_processed" in data
    assert "reports_generated" in data
    assert "cache_hit_rate" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "analytics-service"
    assert data["status"] == "running"
    assert data["port"] == 9013

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "analytics-service"
    assert data["version"] == "1.0.0"

def test_dependencies():
    """Test dependencies endpoint"""
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "cache" in data
    assert "queue" in data
    assert "storage" in data

def test_analytics_status():
    """Test analytics status endpoint"""
    response = client.get("/analytics/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "real_time_enabled" in data
    assert "batch_size" in data

def test_analytics_metrics():
    """Test analytics metrics endpoint"""
    response = client.get("/analytics/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "successful_queries" in data
    assert "failed_queries" in data

def test_execute_query():
    """Test execute query endpoint"""
    response = client.post("/analytics/query", json={"query": "SELECT * FROM data"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "query_id" in data

def test_get_query_result():
    """Test get query result endpoint"""
    response = client.get("/analytics/query/query_123")
    assert response.status_code == 200
    data = response.json()
    assert data["query_id"] == "query_123"
    assert "status" in data

def test_list_reports():
    """Test list reports endpoint"""
    response = client.get("/reports/list")
    assert response.status_code == 200
    data = response.json()
    assert "reports" in data
    assert "total_count" in data
    assert "formats_available" in data

def test_generate_report():
    """Test generate report endpoint"""
    response = client.post("/reports/generate", json={"type": "summary", "format": "json"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "report_id" in data

def test_get_report():
    """Test get report endpoint"""
    response = client.get("/reports/report_123")
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == "report_123"
    assert "status" in data

def test_download_report():
    """Test download report endpoint"""
    response = client.get("/reports/report_123/download")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["report_id"] == "report_123"

def test_delete_report():
    """Test delete report endpoint"""
    response = client.delete("/reports/report_123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["report_id"] == "report_123"

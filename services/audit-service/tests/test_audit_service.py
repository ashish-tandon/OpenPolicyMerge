"""
Tests for Audit Service
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
    assert data["service"] == "audit-service"
    assert data["port"] == 9014

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
    assert "audit_events_logged" in data
    assert "audit_events_processed" in data
    assert "audit_storage_used_bytes" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "audit-service"
    assert data["status"] == "running"
    assert data["port"] == 9014

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "audit-service"
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

def test_audit_status():
    """Test audit status endpoint"""
    response = client.get("/audit/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "real_time_enabled" in data
    assert "retention_days" in data

def test_audit_stats():
    """Test audit stats endpoint"""
    response = client.get("/audit/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "events_today" in data
    assert "storage_used_bytes" in data

def test_log_audit_event():
    """Test log audit event endpoint"""
    response = client.post("/audit/log", json={"event_type": "login", "user_id": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "event_id" in data

def test_get_audit_events():
    """Test get audit events endpoint"""
    response = client.get("/audit/events")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "total_count" in data
    assert "filters_applied" in data

def test_get_audit_event():
    """Test get specific audit event endpoint"""
    response = client.get("/audit/events/audit_123")
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "audit_123"
    assert "timestamp" in data

def test_search_audit_events():
    """Test search audit events endpoint"""
    response = client.post("/audit/search", json={"query": "login", "user_id": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "query" in data
    assert "results" in data

def test_export_audit_data():
    """Test export audit data endpoint"""
    response = client.post("/audit/export", json={"format": "csv", "date_range": "last_30_days"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "export_id" in data

def test_get_export_status():
    """Test get export status endpoint"""
    response = client.get("/audit/export/export_123")
    assert response.status_code == 200
    data = response.json()
    assert data["export_id"] == "export_123"
    assert "status" in data

def test_cleanup_old_audit_data():
    """Test cleanup old audit data endpoint"""
    response = client.post("/audit/cleanup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "records_removed" in data

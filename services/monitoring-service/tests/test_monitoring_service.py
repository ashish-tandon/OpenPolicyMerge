"""
Tests for Monitoring Service
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
    assert data["service"] == "monitoring-service"
    assert data["port"] == 9010

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
    assert "services_monitored" in data
    assert "alerts_triggered" in data
    assert "checks_performed" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "monitoring-service"
    assert data["status"] == "running"
    assert data["port"] == 9010

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "monitoring-service"
    assert data["version"] == "1.0.0"

def test_dependencies():
    """Test dependencies endpoint"""
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "cache" in data
    assert "queue" in data

def test_monitoring_status():
    """Test monitoring status endpoint"""
    response = client.get("/monitoring/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "real_time_enabled" in data
    assert "monitoring_interval" in data

def test_list_monitored_services():
    """Test list monitored services endpoint"""
    response = client.get("/monitoring/services")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "total_count" in data
    assert "healthy_count" in data

def test_get_service_status():
    """Test get service status endpoint"""
    response = client.get("/monitoring/services/test_service")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "test_service"
    assert "status" in data
    assert "last_check" in data

def test_add_service_to_monitor():
    """Test add service to monitor endpoint"""
    response = client.post("/monitoring/services", json={"name": "test_service", "url": "http://localhost:8080"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "service_name" in data

def test_remove_service_from_monitor():
    """Test remove service from monitor endpoint"""
    response = client.delete("/monitoring/services/test_service")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["service_name"] == "test_service"

def test_list_alerts():
    """Test list alerts endpoint"""
    response = client.get("/monitoring/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "total_count" in data
    assert "active_count" in data

def test_create_alert():
    """Test create alert endpoint"""
    response = client.post("/monitoring/alerts", json={"type": "high_cpu", "message": "CPU usage high"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "alert_id" in data

def test_update_alert():
    """Test update alert endpoint"""
    response = client.put("/monitoring/alerts/alert_123", json={"status": "resolved"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["alert_id"] == "alert_123"

def test_delete_alert():
    """Test delete alert endpoint"""
    response = client.delete("/monitoring/alerts/alert_123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["alert_id"] == "alert_123"

def test_get_dashboard_data():
    """Test get dashboard data endpoint"""
    response = client.get("/monitoring/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "system_metrics" in data
    assert "recent_alerts" in data

def test_run_health_checks():
    """Test run health checks endpoint"""
    response = client.post("/monitoring/checks/run")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "checks_run" in data
    assert "healthy_count" in data

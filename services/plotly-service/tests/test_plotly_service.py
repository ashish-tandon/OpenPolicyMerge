"""
Tests for Plotly Service
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
    assert data["service"] == "plotly-service"
    assert data["port"] == 9011

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
    assert "charts_generated" in data
    assert "charts_exported" in data
    assert "cache_hit_rate" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "plotly-service"
    assert data["status"] == "running"
    assert data["port"] == 9011

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "plotly-service"
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

def test_plotly_status():
    """Test plotly status endpoint"""
    response = client.get("/plotly/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "theme" in data
    assert "dark_mode_enabled" in data

def test_list_charts():
    """Test list charts endpoint"""
    response = client.get("/plotly/charts")
    assert response.status_code == 200
    data = response.json()
    assert "charts" in data
    assert "total_count" in data
    assert "cached_count" in data

def test_create_chart():
    """Test create chart endpoint"""
    response = client.post("/plotly/charts/create", json={"type": "line", "data": [1, 2, 3]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "chart_id" in data

def test_get_chart():
    """Test get chart endpoint"""
    response = client.get("/plotly/charts/chart_123")
    assert response.status_code == 200
    data = response.json()
    assert data["chart_id"] == "chart_123"
    assert "chart_type" in data

def test_update_chart():
    """Test update chart endpoint"""
    response = client.put("/plotly/charts/chart_123", json={"data": [4, 5, 6]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chart_id"] == "chart_123"

def test_delete_chart():
    """Test delete chart endpoint"""
    response = client.delete("/plotly/charts/chart_123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chart_id"] == "chart_123"

def test_export_chart():
    """Test export chart endpoint"""
    response = client.post("/plotly/charts/chart_123/export", json={"format": "png"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chart_id"] == "chart_123"
    assert "format" in data

def test_download_chart():
    """Test download chart endpoint"""
    response = client.get("/plotly/charts/chart_123/download", params={"format": "png"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chart_id"] == "chart_123"

def test_create_chart_template():
    """Test create chart template endpoint"""
    response = client.post("/plotly/templates", json={"name": "line_template", "config": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "template_id" in data

def test_list_chart_templates():
    """Test list chart templates endpoint"""
    response = client.get("/plotly/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert "total_count" in data

def test_get_chart_template():
    """Test get chart template endpoint"""
    response = client.get("/plotly/templates/template_123")
    assert response.status_code == 200
    data = response.json()
    assert data["template_id"] == "template_123"
    assert "name" in data

def test_validate_data():
    """Test validate data endpoint"""
    response = client.post("/plotly/data/validate", json={"x": [1, 2, 3], "y": [4, 5, 6]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "valid" in data

def test_clean_data():
    """Test clean data endpoint"""
    response = client.post("/plotly/data/clean", json={"data": [1, None, 3, "invalid", 5]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "original_count" in data
    assert "cleaned_count" in data

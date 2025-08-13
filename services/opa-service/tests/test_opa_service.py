"""
Tests for OPA Service
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
    assert data["service"] == "opa-service"
    assert data["port"] == 8181

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
    assert "policy_evaluations" in data
    assert "policy_cache_hits" in data
    assert "active_policies" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "opa-service"
    assert data["status"] == "running"
    assert data["port"] == 8181

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "opa-service"
    assert data["version"] == "1.0.0"

def test_dependencies():
    """Test dependencies endpoint"""
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "opa_engine" in data
    assert "policy_store" in data
    assert "database" in data

def test_opa_status():
    """Test OPA status endpoint"""
    response = client.get("/opa/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "engine_version" in data
    assert "policy_count" in data

def test_list_policies():
    """Test list policies endpoint"""
    response = client.get("/opa/policies")
    assert response.status_code == 200
    data = response.json()
    assert "policies" in data
    assert "total_count" in data

def test_create_policy():
    """Test create policy endpoint"""
    response = client.post("/opa/policies", json={"name": "test_policy", "content": "package test"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "policy_id" in data

def test_get_policy():
    """Test get policy endpoint"""
    response = client.get("/opa/policies/policy_123")
    assert response.status_code == 200
    data = response.json()
    assert data["policy_id"] == "policy_123"
    assert "name" in data

def test_update_policy():
    """Test update policy endpoint"""
    response = client.put("/opa/policies/policy_123", json={"content": "package updated"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["policy_id"] == "policy_123"

def test_delete_policy():
    """Test delete policy endpoint"""
    response = client.delete("/opa/policies/policy_123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["policy_id"] == "policy_123"

def test_evaluate_policy():
    """Test evaluate policy endpoint"""
    response = client.post("/opa/evaluate", json={"policy": "test", "input": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "result" in data

def test_get_data():
    """Test get data endpoint"""
    response = client.get("/opa/data")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total_entries" in data

def test_set_data():
    """Test set data endpoint"""
    response = client.post("/opa/data", json={"key": "value"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_clear_data():
    """Test clear data endpoint"""
    response = client.delete("/opa/data")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_query_data():
    """Test query data endpoint"""
    response = client.get("/opa/query", params={"query": "data.test"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "query" in data

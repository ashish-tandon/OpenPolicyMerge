"""
Tests for Queue Service
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
    assert data["service"] == "queue-service"
    assert data["port"] == 9017

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
    assert "queue_size" in data
    assert "active_workers" in data
    assert "tasks_processed" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "queue-service"
    assert data["status"] == "running"
    assert data["port"] == 9017

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "queue-service"
    assert data["version"] == "1.0.0"

def test_dependencies():
    """Test dependencies endpoint"""
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "rabbitmq" in data
    assert "database" in data
    assert "cache" in data

def test_queue_status():
    """Test queue status endpoint"""
    response = client.get("/queue/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert "rabbitmq_host" in data
    assert "rabbitmq_port" in data

def test_queue_stats():
    """Test queue stats endpoint"""
    response = client.get("/queue/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_queues" in data
    assert "total_messages" in data
    assert "active_workers" in data

def test_list_queues():
    """Test list queues endpoint"""
    response = client.get("/queue/queues")
    assert response.status_code == 200
    data = response.json()
    assert "queues" in data
    assert "total_count" in data

def test_publish_message():
    """Test publish message endpoint"""
    response = client.post("/queue/publish", json={"message": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message_id" in data

def test_consume_message():
    """Test consume message endpoint"""
    response = client.get("/queue/consume")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message_id" in data

def test_acknowledge_message():
    """Test acknowledge message endpoint"""
    response = client.post("/queue/ack", json={"message_id": "test_123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message_id"] == "test_123"

def test_negative_acknowledge():
    """Test negative acknowledge endpoint"""
    response = client.post("/queue/nack", json={"message_id": "test_123", "requeue": True})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message_id"] == "test_123"

def test_purge_queue():
    """Test purge queue endpoint"""
    response = client.post("/queue/purge")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "messages_removed" in data

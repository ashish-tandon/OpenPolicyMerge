"""
Tests for MCP Service
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
    assert data["service"] == "mcp-service"
    assert data["port"] == 9012

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
    assert "requests_total" in data
    assert "errors_total" in data
    assert "response_time_avg" in data

def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "mcp-service"
    assert data["status"] == "running"
    assert data["port"] == 9012

def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "mcp-service"
    assert data["version"] == "1.0.0"

def test_dependencies():
    """Test dependencies endpoint"""
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "cache" in data
    assert "queue" in data

def test_mcp_status():
    """Test MCP status endpoint"""
    response = client.get("/mcp/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "protocol_version" in data

def test_mcp_models():
    """Test MCP models endpoint"""
    response = client.get("/mcp/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "total_count" in data

def test_mcp_generate():
    """Test MCP generate endpoint"""
    response = client.post("/mcp/generate", json={"prompt": "Hello", "model": "gpt-4"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data

def test_mcp_chat():
    """Test MCP chat endpoint"""
    response = client.post("/mcp/chat", json={"messages": [{"role": "user", "content": "Hello"}]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data

def test_mcp_embed():
    """Test MCP embed endpoint"""
    response = client.post("/mcp/embed", json={"text": "Hello world"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "embeddings" in data

def test_mcp_stream():
    """Test MCP stream endpoint"""
    response = client.post("/mcp/stream", json={"prompt": "Hello", "model": "gpt-4"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "stream_id" in data

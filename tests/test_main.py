"""Tests for the main API."""
from fastapi.testclient import TestClient

from truapi.drivers.rest.main import app

client = TestClient(app)


def test_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["name"] == "TruAPI"
    assert "version" in data
    assert "environment" in data


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_users_endpoint_accessible():
    """Test that users API is accessible."""
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data

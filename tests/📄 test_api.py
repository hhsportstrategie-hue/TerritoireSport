"""
Tests automatisés de l'API
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    """Test endpoint health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root_serves_frontend():
    """Test que le frontend est servi."""
    response = client.get("/")
    assert response.status_code == 200

def test_clubs_endpoint():
    """Test endpoint clubs."""
    response = client.get("/api/clubs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_partners_endpoint():
    """Test endpoint partners."""
    response = client.get("/api/partners/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_territory_endpoint():
    """Test endpoint territory."""
    response = client.get("/api/territory/")
    assert response.status_code == 200

def test_auth_required():
    """Test que l'auth fonctionne (quand activée)."""
    response = client.get("/api/protected")
    assert response.status_code in [401, 404]

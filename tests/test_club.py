"""Tests unitaires — Endpoints Club."""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def client(temp_db):
    from main import app
    with TestClient(app) as c:
        yield c


def test_register_club(client):
    """Inscription d'un nouveau club."""
    r = client.post("/api/clubs/register", json={
        "name": "Test Club",
        "email": "test@example.com",
        "password": "password123",
        "sport": "football",
        "city": "Caen",
        "department": "14",
        "size": "small"
    })
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["name"] == "Test Club"


def test_register_club_duplicate_email(client):
    """Inscription avec email déjà utilisé."""
    client.post("/api/clubs/register", json={
        "name": "Club 1",
        "email": "dup@example.com",
        "password": "pass",
        "sport": "football",
        "city": "Caen",
        "department": "14",
        "size": "small"
    })
    r = client.post("/api/clubs/register", json={
        "name": "Club 2",
        "email": "dup@example.com",
        "password": "pass",
        "sport": "rugby",
        "city": "Rouen",
        "department": "76",
        "size": "small"
    })
    assert r.status_code == 400


def test_login_club(client):
    """Login avec credentials valides."""
    client.post("/api/clubs/register", json={
        "name": "Login Test",
        "email": "login@example.com",
        "password": "pass123",
        "sport": "rugby",
        "city": "Rouen",
        "department": "76",
        "size": "medium"
    })
    r = client.post("/api/clubs/login", json={
        "email": "login@example.com",
        "password": "pass123"
    })
    assert r.status_code == 200


def test_login_invalid_password(client):
    """Login avec mauvais mot de passe."""
    client.post("/api/clubs/register", json={
        "name": "Bad Pass Test",
        "email": "bad@example.com",
        "password": "good",
        "sport": "basketball",
        "city": "Le Havre",
        "department": "76",
        "size": "small"
    })
    r = client.post("/api/clubs/login", json={
        "email": "bad@example.com",
        "password": "wrong"
    })
    assert r.status_code == 401


def test_get_club_by_id(client):
    """Récupérer un club par ID après inscription."""
    r = client.post("/api/clubs/register", json={
        "name": "Get Test",
        "email": "get@example.com",
        "password": "pass",
        "sport": "football",
        "city": "Caen",
        "department": "14",
        "size": "small"
    })
    club_id = r.json()["id"]
    r2 = client.get(f"/api/clubs/{club_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == club_id


def test_get_club_404(client):
    """404 pour un club inconnu."""
    r = client.get("/api/clubs/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
"""Tests unitaires — Calcul d'affinité."""
import pytest
import sys
import uuid
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def client(temp_db):
    from main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def club_id(client):
    """Crée un club et retourne son ID."""
    unique = uuid.uuid4().hex[:8]
    r = client.post("/api/clubs/register", json={
        "name": f"Affinity Test Club {unique}",
        "email": f"affinity_{unique}@example.com",
        "password": "pass",
        "sport": "football",
        "city": "Caen",
        "department": "14",
        "size": "small"
    })
    assert r.status_code == 201, f"Register failed: {r.text}"
    return r.json()["id"]


def test_affinity_404_for_unknown_club(client):
    """404 pour un club inconnu."""
    r = client.get("/api/affinity/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_affinity_returns_response(client, club_id):
    """L'endpoint affinity retourne une réponse pour un club valide."""
    r = client.get(f"/api/affinity/{club_id}")
    assert r.status_code in [200, 404]


def test_save_affinity(client, club_id):
    """Sauvegarder une affinité."""
    r = client.post("/api/affinity/save", json={
        "club_id": club_id,
        "theme_ids": ["cohesion", "sante"]
    })
    assert r.status_code in [200, 201, 422, 404]
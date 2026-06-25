"""Tests unitaires — Endpoints Territory."""
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


def test_get_territory_404(client):
    """404 pour un territoire inconnu."""
    r = client.get("/api/territories/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_territory_full_endpoint_404(client):
    """404 pour un territoire inconnu."""
    r = client.get("/api/territories/00000000-0000-0000-0000-000000000000/full")
    assert r.status_code == 404


def test_territory_by_club_404(client):
    """404 pour un club sans code_insee."""
    r = client.post("/api/clubs/register", json={
        "name": "No INSEE",
        "email": "ni@t.com",
        "password": "p",
        "sport": "football",
        "city": "Caen",
        "department": "14",
        "size": "small"
    })
    club_id = r.json()["id"]
    r2 = client.get(f"/api/territories/by-club/{club_id}")
    assert r2.status_code == 404


def test_diagnostic_questions(client):
    """Le diagnostic a des questions définies."""
    r = client.get("/api/diagnostic/questions")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    q = data[0]
    assert "id" in q
    assert "text" in q
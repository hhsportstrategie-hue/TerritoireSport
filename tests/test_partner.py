"""Tests unitaires — Endpoints Partner."""
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


def test_list_partners_returns_list(client):
    """Liste des partenaires retourne une liste."""
    r = client.get("/api/partners/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_partners_have_required_fields(client):
    """Les partenaires ont les champs obligatoires."""
    r = client.get("/api/partners/")
    partners = r.json()
    if partners:
        p = partners[0]
        assert "name" in p
        assert "type" in p
        assert "category" in p


def test_filter_partners_by_type(client):
    """Filtrer les partenaires par type public."""
    r = client.get("/api/partners/?type=public")
    assert r.status_code == 200
    partners = r.json()
    for p in partners:
        assert p["type"] == "public"


def test_filter_partners_by_department(client):
    """Filtrer les partenaires par département."""
    r = client.get("/api/partners/?department=14")
    assert r.status_code == 200
    partners = r.json()
    for p in partners:
        assert p["department"] == "14"


def test_filter_partners_by_theme(client):
    """Filtrer les partenaires par thème."""
    r = client.get("/api/partners/?theme=cohesion")
    assert r.status_code == 200
    partners = r.json()
    for p in partners:
        assert "cohesion" in p.get("themes", []) or p.get("category") == "cohesion"
"""Tests d'intégration — Endpoints API."""
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


def test_health(client):
    """Endpoint /api/health répond OK."""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root_serves_index(client):
    """La racine sert index.html."""
    r = client.get("/")
    assert r.status_code == 200


def test_dashboard_html(client):
    """Le dashboard est servi."""
    r = client.get("/dashboard.html")
    assert r.status_code == 200


def test_admin_info(client):
    """Endpoint /api/admin/info retourne les infos système."""
    r = client.get("/api/admin/info")
    assert r.status_code == 200
    data = r.json()
    assert "db_path" in data


def test_admin_seed_is_idempotent(client):
    """Endpoint /api/admin/seed peut être appelé plusieurs fois."""
    r1 = client.post("/api/admin/seed")
    assert r1.status_code == 200
    r2 = client.post("/api/admin/seed")
    assert r2.status_code == 200


def test_admin_reset(client):
    """Endpoint /api/admin/reset réinitialise la DB."""
    r = client.post("/api/admin/reset")
    assert r.status_code == 200


def test_diagnostic_questions(client):
    """Endpoint /api/diagnostic/questions retourne les questions."""
    r = client.get("/api/diagnostic/questions")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_projects_themes(client):
    """Endpoint /api/projects/themes retourne les thèmes."""
    r = client.get("/api/projects/themes")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_projects_cas_inspirants(client):
    """Endpoint /api/projects/cas-inspirants retourne les cas inspirants."""
    r = client.get("/api/projects/cas-inspirants")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
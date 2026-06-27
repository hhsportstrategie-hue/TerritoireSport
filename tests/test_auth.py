"""Tests unitaires — Authentification API."""
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


# ════════════════════════════════════════════════════════════════
# Tests WHOAMI (sans générer de token partenaire)
# ════════════════════════════════════════════════════════════════

def test_whoami_no_token_returns_401(client):
    """whoami sans token → 401."""
    r = client.get("/api/auth/whoami")
    assert r.status_code == 401


def test_whoami_invalid_token_returns_401(client):
    """whoami avec token bidon → 401."""
    r = client.get("/api/auth/whoami", headers={"X-API-Key": "token_bidon"})
    assert r.status_code == 401


def test_whoami_with_admin_token_returns_admin(client):
    """whoami avec le token admin → type=admin."""
    r = client.get("/api/auth/whoami", headers={"X-API-Key": "territoire-sport-demo-2026"})
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "admin"
    assert data["client_name"] == "admin"
    assert data["remaining_today"] == "illimité"


def test_whoami_accepts_bearer_format(client):
    """whoami accepte aussi Authorization: Bearer."""
    r = client.get("/api/auth/whoami", headers={"Authorization": "Bearer territoire-sport-demo-2026"})
    assert r.status_code == 200
    assert r.json()["type"] == "admin"


# ════════════════════════════════════════════════════════════════
# Tests création de tokens (admin only)
# ════════════════════════════════════════════════════════════════

def test_create_token_requires_admin(client):
    """Créer un token sans auth → 401."""
    r = client.post("/api/auth/token?client_name=Test")
    assert r.status_code == 401


def test_create_token_with_admin_returns_token(client):
    """Admin crée un token → reçoit le token en clair."""
    r = client.post(
        "/api/auth/token",
        params={"client_name": "SM Caen", "quota": 500},
        headers={"X-API-Key": "territoire-sport-demo-2026"}
    )
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert len(data["token"]) > 30  # URL-safe token
    assert data["client_name"] == "SM Caen"
    assert data["quota_per_day"] == 500
    assert "warning" in data  # Rappel que c'est la seule fois


# ════════════════════════════════════════════════════════════════
# Tests cycle complet : création → utilisation → whoami
# ════════════════════════════════════════════════════════════════

def test_full_token_lifecycle(client):
    """Cycle complet : admin crée token → partenaire l'utilise → whoami fonctionne."""
    # 1. Admin crée un token
    r = client.post(
        "/api/auth/token",
        params={"client_name": "FC Rouen", "client_email": "test@fc-rouen.fr", "quota": 100},
        headers={"X-API-Key": "territoire-sport-demo-2026"}
    )
    assert r.status_code == 200
    partner_token = r.json()["token"]

    # 2. Le partenaire utilise son token sur whoami
    r = client.get("/api/auth/whoami", headers={"X-API-Key": partner_token})
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "partner"
    assert data["client_name"] == "FC Rouen"
    assert data["quota_per_day"] == 100
    assert data["used_today"] == 1
    assert data["remaining_today"] == 99

    # 3. Le partenaire utilise une route publique avec son token
    r = client.get("/api/shortlist?page_size=5", headers={"X-API-Key": partner_token})
    assert r.status_code == 200  # Le shortlist reste public


def test_partner_token_increments_usage(client):
    """Chaque appel avec le token partenaire incrémente le compteur."""
    r = client.post(
        "/api/auth/token",
        params={"client_name": "Test Usage", "quota": 100},
        headers={"X-API-Key": "territoire-sport-demo-2026"}
    )
    token = r.json()["token"]

    # 3 appels whoami avec le token partenaire
    for i in range(3):
        client.get("/api/auth/whoami", headers={"X-API-Key": token})

    # Le 4e appel doit montrer used_today=4 (3 whoami + 1 de ce 4e appel)
    r = client.get("/api/auth/whoami", headers={"X-API-Key": token})
    assert r.json()["used_today"] == 4
    assert r.json()["remaining_today"] == 96


# ════════════════════════════════════════════════════════════════
# Tests admin/usage
# ════════════════════════════════════════════════════════════════

def test_usage_stats_requires_admin(client):
    """Stats d'usage nécessitent l'admin."""
    r = client.get("/api/admin/usage")
    assert r.status_code == 401


def test_usage_stats_returns_tokens(client):
    """Stats d'usage admin retourne la liste des tokens."""
    # Créer 2 tokens
    for name in ["Club A", "Club B"]:
        client.post(
            "/api/auth/token",
            params={"client_name": name},
            headers={"X-API-Key": "territoire-sport-demo-2026"}
        )

    r = client.get("/api/admin/usage", headers={"X-API-Key": "territoire-sport-demo-2026"})
    assert r.status_code == 200
    data = r.json()
    assert "tokens" in data
    assert data["active_tokens"] >= 2
    assert any(t["client_name"] == "Club A" for t in data["tokens"])


# ════════════════════════════════════════════════════════════════
# Test rate limit + auth combinés
# ════════════════════════════════════════════════════════════════

def test_token_with_zero_quota_rejected(client):
    """Token avec quota=0 → toutes les requêtes rejetées."""
    # Note: on ne peut pas créer de token avec quota=0 (min 1),
    # donc on simule en désactivant le token après création.
    r = client.post(
        "/api/auth/token",
        params={"client_name": "Disabled Soon", "quota": 1},
        headers={"X-API-Key": "territoire-sport-demo-2026"}
    )
    token = r.json()["token"]

    # 1er appel OK
    r = client.get("/api/auth/whoami", headers={"X-API-Key": token})
    assert r.status_code == 200

    # 2e appel : quota dépassé
    r = client.get("/api/auth/whoami", headers={"X-API-Key": token})
    assert r.status_code == 429
    assert "Quota" in r.json()["detail"]

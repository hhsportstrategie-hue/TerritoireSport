"""Tests unitaires — Endpoint /api/shortlist (pagination, filtres, tri)."""
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


def test_shortlist_returns_paginated_structure(client):
    """La réponse shortlist contient pagination + filters_applied."""
    r = client.get("/api/shortlist")
    assert r.status_code == 200
    data = r.json()
    assert "shortlist" in data
    assert "pagination" in data
    assert "filters_applied" in data


def test_shortlist_default_page_size_is_20(client):
    """Par défaut, page=1 et page_size=20."""
    r = client.get("/api/shortlist")
    data = r.json()
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 20


def test_shortlist_pagination_consistency(client):
    """Le total est >= au nombre de résultats de la page courante."""
    r = client.get("/api/shortlist?page=1&page_size=5")
    data = r.json()
    assert data["pagination"]["total"] >= len(data["shortlist"])
    assert len(data["shortlist"]) <= 5


def test_shortlist_has_next_when_more_pages(client):
    """has_next=True si on n'est pas sur la dernière page."""
    r = client.get("/api/shortlist?page=1&page_size=1")
    data = r.json()
    if data["pagination"]["total_pages"] > 1:
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_prev"] is False


def test_shortlist_page_2_returns_different_items(client):
    """La page 2 contient des items différents de la page 1."""
    r1 = client.get("/api/shortlist?page=1&page_size=2&sort=score")
    r2 = client.get("/api/shortlist?page=2&page_size=2&sort=score")
    ids1 = [item["id"] for item in r1.json()["shortlist"]]
    ids2 = [item["id"] for item in r2.json()["shortlist"]]
    assert set(ids1).isdisjoint(set(ids2))


def test_shortlist_sort_by_name(client):
    """Tri par nom = ordre alphabétique."""
    r = client.get("/api/shortlist?sort=name&page=1&page_size=100")
    names = [item["name"] for item in r.json()["shortlist"]]
    assert names == sorted(names)


def test_shortlist_invalid_sort_rejected(client):
    """Tri invalide → erreur 400."""
    r = client.get("/api/shortlist?sort=evil_drop_table")
    assert r.status_code == 400


def test_shortlist_invalid_type_rejected(client):
    """Type invalide → erreur 400."""
    r = client.get("/api/shortlist?type=banana")
    assert r.status_code == 400


def test_shortlist_search_filters_results(client):
    """La recherche réduit le nombre de résultats."""
    r_all = client.get("/api/shortlist?page=1&page_size=100")
    r_search = client.get("/api/shortlist?search=argentan&page=1&page_size=100")
    total_all = r_all.json()["pagination"]["total"]
    total_search = r_search.json()["pagination"]["total"]
    # Soit la recherche trouve des résultats, soit 0
    assert total_search <= total_all


def test_shortlist_filters_applied_echoed(client):
    """Les filtres sont renvoyés dans filters_applied."""
    r = client.get("/api/shortlist?theme=1&type=public&sort=name")
    filters = r.json()["filters_applied"]
    assert filters["theme"] == 1
    assert filters["type"] == "public"
    assert filters["sort"] == "name"


def test_shortlist_page_size_too_large_rejected(client):
    """page_size > 100 rejeté par FastAPI."""
    r = client.get("/api/shortlist?page_size=500")
    assert r.status_code == 422  # Validation error


def test_shortlist_page_zero_rejected(client):
    """page=0 rejeté par FastAPI."""
    r = client.get("/api/shortlist?page=0")
    assert r.status_code == 422

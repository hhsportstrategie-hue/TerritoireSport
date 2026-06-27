"""Tests unitaires — Export PDF."""
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
# Tests du module pdf_export directement
# ════════════════════════════════════════════════════════════════

def test_generate_pdf_with_empty_list():
    """PDF généré même sans partenaire."""
    from pdf_export import generate_shortlist_pdf
    pdf_bytes = generate_shortlist_pdf([], {"commune": None, "theme": None, "theme_label": "", "type": None, "search": None})
    assert pdf_bytes[:4] == b"%PDF"  # Magic bytes
    assert len(pdf_bytes) > 1000  # Au moins la page de garde


def test_generate_pdf_with_partners():
    """PDF généré avec des partenaires contient bien des données."""
    from pdf_export import generate_shortlist_pdf
    partners = [
        {
            "name": "Test Club A",
            "type": "association",
            "category": "club",
            "city": "Caen",
            "commune": "Caen",
            "themes": '["sport_sante", "insertion"]',
            "score": 85,
            "contact_email": "test@caen.fr",
            "contact_url": None,
            "description": "Description test"
        },
        {
            "name": "Test Entreprise B",
            "type": "company",
            "category": "entreprise",
            "city": "Rouen",
            "commune": "Rouen",
            "themes": '["environnement"]',
            "score": 45,
            "contact_email": None,
            "contact_url": "https://example.com",
            "description": None
        },
    ]
    filters = {"commune": "caen", "theme": 1, "theme_label": "Sport & Santé", "type": None, "search": None}
    pdf_bytes = generate_shortlist_pdf(partners, filters, commune_label="Caen")

    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 3000  # Doit être plus gros avec tableau


def test_get_theme_label_returns_label():
    """get_theme_label retourne un libellé lisible."""
    from pdf_export import get_theme_label
    assert get_theme_label(1) == "Sport & Santé"
    assert get_theme_label(2) == "Insertion / Cohésion Sociale"
    assert get_theme_label(99) == ""  # Inconnu → vide


def test_score_color_thresholds():
    """Les couleurs de score reflètent bien les seuils."""
    from pdf_export import _score_color
    from reportlab.lib import colors

    # Score élevé → vert
    c_high = _score_color(85)
    # Score moyen → orange
    c_mid = _score_color(55)
    # Score faible → rouge
    c_low = _score_color(20)

    # Vérifier juste que ce sont des couleurs différentes
    assert c_high is not c_mid
    assert c_mid is not c_low


# ════════════════════════════════════════════════════════════════
# Tests de l'endpoint /api/shortlist/pdf
# ════════════════════════════════════════════════════════════════

def test_pdf_endpoint_returns_pdf(client):
    """L'endpoint renvoie bien un PDF (Content-Type + magic bytes)."""
    r = client.get("/api/shortlist/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    # Le contenu commence par %PDF
    assert r.content[:4] == b"%PDF"


def test_pdf_endpoint_with_commune_filter(client):
    """Filtre par commune est transmis au PDF."""
    r = client.get("/api/shortlist/pdf?commune=caen")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    # Le filename doit contenir la commune
    cd = r.headers.get("content-disposition", "")
    assert "caen" in cd.lower()


def test_pdf_endpoint_with_theme_filter(client):
    """Filtre par thématique fonctionne."""
    r = client.get("/api/shortlist/pdf?theme=1")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"


def test_pdf_endpoint_with_type_filter(client):
    """Filtre par type fonctionne."""
    r = client.get("/api/shortlist/pdf?type=public")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"


def test_pdf_endpoint_with_search(client):
    """Recherche full-text fonctionne."""
    r = client.get("/api/shortlist/pdf?search=argentan")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"


def test_pdf_endpoint_invalid_type_rejected(client):
    """Type invalide → 400."""
    r = client.get("/api/shortlist/pdf?type=banana")
    assert r.status_code == 400


def test_pdf_endpoint_max_results_limit(client):
    """max_results > 200 rejeté."""
    r = client.get("/api/shortlist/pdf?max_results=1000")
    assert r.status_code == 422  # FastAPI validation


def test_pdf_endpoint_filename_includes_date(client):
    """Le nom de fichier contient la date du jour."""
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")
    r = client.get("/api/shortlist/pdf")
    assert today in r.headers["content-disposition"]


def test_pdf_endpoint_filename_for_commune(client):
    """Le nom de fichier contient la commune si spécifiée."""
    r = client.get("/api/shortlist/pdf?commune=caen")
    cd = r.headers["content-disposition"]
    assert "caen" in cd.lower()
    assert ".pdf" in cd

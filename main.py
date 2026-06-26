"""
TerritoireSport — API principale
Version complète avec tous les endpoints essentiels.
"""
import os
import sqlite3
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List

from db_config import DB_PATH
from auth import verify_token, API_TOKEN
from cache import cached
from metrics import track_request, get_metrics
from pagination import pagination_params
from rate_limit import check_rate_limit
from csv_export import router as csv_router


# ── Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_file = Path(DB_PATH)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Appliquer le schéma
    schema_path = Path("data/schema.sql")
    if schema_path.exists():
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(schema_path.read_text())
        conn.commit()
        conn.close()

    # Seed si la DB est vide
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM clubs")
    count = cur.fetchone()[0]
    conn.close()

    if count == 0:
        import seed
        seed.seed()

    yield
        conn.commit()
        conn.close()

    # Seed si la DB est vide
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM clubs")
    count = cur.fetchone()[0]
    conn.close()

    if count == 0:
        import seed
        seed.seed()

    yield
    yield


# ── App ──────────────────────────────────────────────────────────
app = FastAPI(
    title="TerritoireSport API",
    description="API pour la plateforme TerritoireSport - Sport & Territoire",
    version="3.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router CSV
app.include_router(csv_router)


# ── Middleware métriques ─────────────────────────────────────────
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Track toutes les requêtes."""
    import time
    start = time.time()
    error = False
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            error = True
        return response
    except Exception:
        error = True
        raise
    finally:
        duration = time.time() - start
        track_request(request.url.path, duration, error)


# ── Endpoints de base ────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": "3.0.0",
        "service": "TerritoireSport API",
        "endpoints": [
            "/api/health",
            "/api/ping",
            "/api/communes",
            "/api/themes",
            "/api/stats",
            "/api/shortlist",
            "/api/export/clubs.csv",
            "/api/export/partners.csv",
            "/api/metrics"
        ]
    }


@app.get("/api/health")
async def health():
    """Health check."""
    db_exists = Path(DB_PATH).exists()
    return {
        "status": "healthy" if db_exists else "degraded",
        "db_path": DB_PATH,
        "db_exists": db_exists
    }


@app.get("/api/ping")
async def ping():
    return {"pong": True}


# ── Endpoints données ────────────────────────────────────────────
@app.get("/api/themes")
async def get_themes():
    """Liste des 19 thématiques sociétales."""
    themes = [
        {"id": 1, "name": "Sport & Santé", "color": "#10b981"},
        {"id": 2, "name": "Insertion / Cohésion Sociale", "color": "#3b82f6"},
        {"id": 3, "name": "Environnement", "color": "#22c55e"},
        {"id": 4, "name": "Éducation / Jeunesse", "color": "#f59e0b"},
        {"id": 5, "name": "Culture / Patrimoine", "color": "#8b5cf6"},
        {"id": 6, "name": "Économie Locale / Emploi", "color": "#ef4444"},
        {"id": 7, "name": "Citoyenneté", "color": "#6366f1"},
        {"id": 8, "name": "Innovation / Technologie", "color": "#06b6d4"},
        {"id": 9, "name": "Alimentation", "color": "#84cc16"},
        {"id": 10, "name": "Tourisme", "color": "#f97316"},
        {"id": 11, "name": "Intergénérationnel", "color": "#ec4899"},
        {"id": 12, "name": "Handicap", "color": "#14b8a6"},
        {"id": 13, "name": "Éducation Populaire", "color": "#a855f7"},
        {"id": 14, "name": "Santé Mentale", "color": "#0ea5e9"},
        {"id": 15, "name": "Égalité des Chances", "color": "#d946ef"},
        {"id": 16, "name": "Écologie", "color": "#16a34a"},
        {"id": 17, "name": "Patrimoine Immatériel", "color": "#7c3aed"},
        {"id": 18, "name": "Innovation Sociale", "color": "#0891b2"},
        {"id": 19, "name": "Urgence Sociale", "color": "#dc2626"}
    ]
    return {"themes": themes, "count": len(themes)}


@app.get("/api/stats")
async def get_stats():
    """Statistiques globales."""
    if not Path(DB_PATH).exists():
        return {"error": "Database not found"}

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    stats = {}

    # Clubs
    cur.execute("SELECT COUNT(*) FROM clubs")
    stats["clubs_count"] = cur.fetchone()[0]

    # Partenaires
    cur.execute("SELECT COUNT(*) FROM partners")
    stats["partners_count"] = cur.fetchone()[0]

    # Projets
    cur.execute("SELECT COUNT(*) FROM projects")
    stats["projects_count"] = cur.fetchone()[0]

    # Communes
    cur.execute("SELECT COUNT(DISTINCT commune) FROM clubs")
    stats["communes_count"] = cur.fetchone()[0]

    # EPCI
    cur.execute("SELECT COUNT(DISTINCT epci) FROM clubs WHERE epci IS NOT NULL")
    stats["epci_count"] = cur.fetchone()[0]

    conn.close()
    return stats


@app.get("/api/communes")
async def get_communes(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None
):
    """Liste des communes avec clubs."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if search:
        cur.execute(
            "SELECT DISTINCT commune, COUNT(*) as clubs_count FROM clubs WHERE commune LIKE ? GROUP BY commune ORDER BY commune LIMIT ? OFFSET ?",
            (f"%{search}%", limit, offset)
        )
    else:
        cur.execute(
            "SELECT DISTINCT commune, COUNT(*) as clubs_count FROM clubs GROUP BY commune ORDER BY commune LIMIT ? OFFSET ?",
            (limit, offset)
        )

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return {"communes": rows, "count": len(rows), "limit": limit, "offset": offset}


@app.get("/api/shortlist")
async def get_shortlist(
    commune: Optional[str] = None,
    theme: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Shortlist des partenaires potentiels."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
        SELECT p.*, c.name as club_name, c.commune
        FROM partners p
        LEFT JOIN clubs c ON p.club_id = c.id
        WHERE 1=1
    """
    params = []

    if commune:
        query += " AND c.commune = ?"
        params.append(commune)

    if theme:
        query += " AND p.theme_id = ?"
        params.append(theme)

    query += " ORDER BY p.score DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return {"shortlist": rows, "count": len(rows)}


@app.get("/api/metrics")
async def metrics():
    """Métriques de l'API."""
    return get_metrics()
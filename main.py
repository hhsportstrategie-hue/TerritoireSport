"""
TerritoireSport — API principale
Version complète avec tous les endpoints essentiels.
"""
import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from typing import Optional, List

from db_config import DB_PATH
from auth import verify_token, API_TOKEN, generate_partner_token
from cache import cached
from metrics import track_request, get_metrics
from pagination import pagination_params
from rate_limit import check_rate_limit
from csv_export import router as csv_router
from pdf_export import generate_shortlist_pdf, get_theme_label


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
        import init_db
        init_db.init_db()
        import seed
        seed.seed()

    # Initialiser les tables d'auth API
    from auth import _init_tokens_table, init_usage_table
    _init_tokens_table()
    init_usage_table()

    # Initialiser les tables du parcours utilisateur
    from parcours import init_parcours_tables
    init_parcours_tables()

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

# Router parcours utilisateur
from parcours import router as parcours_router
app.include_router(parcours_router)


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
    
    return {
        "club_id": club_id,
        "name": name,
        "sport": sport,
        "commune": commune,
        "departement": departement_code,
        "niveau": niveau,
        "licencies": licencies,
        "latitude": latitude,
        "longitude": longitude,
        "epci": epci_name,
        "code_insee": code_insee,
        "status": "registered"
    }


@app.get("/api/communes/all")
async def get_all_communes(
    limit: int = Query(100, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    department: Optional[str] = None,
    search: Optional[str] = None
):
    """Liste de toutes les communes normandes (referentiel geographique)."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM communes WHERE 1=1"
    params = []

    if department:
        query += " AND department = ?"
        params.append(department)

    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")

    query += " ORDER BY population DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return {"communes": rows, "count": len(rows), "limit": limit, "offset": offset}


@app.get("/api/communes/{code_insee}")
async def get_commune_by_code(code_insee: str):
    """Detail d'une commune par code INSEE."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM communes WHERE code_insee = ?", (code_insee,))
    commune = cur.fetchone()

    if not commune:
        conn.close()
        raise HTTPException(status_code=404, detail="Commune not found")

    # Clubs dans cette commune
    cur.execute("SELECT id, name, sport FROM clubs WHERE commune = ?", (commune["name"],))
    clubs = [dict(row) for row in cur.fetchall()]

    # Partenaires dans cette commune
    cur.execute("SELECT id, name, type, category FROM partners WHERE city = ?", (commune["name"],))
    partners = [dict(row) for row in cur.fetchall()]

    conn.close()
    return {
        "commune": dict(commune),
        "clubs": clubs,
        "partners": partners
    }

    return {"communes": rows, "count": len(rows), "limit": limit, "offset": offset}


@app.get("/api/shortlist")
async def get_shortlist(
    commune: Optional[str] = None,
    theme: Optional[int] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de page"),
    sort: str = Query("score", description="Tri: score|name|type")
):
    """Shortlist paginée des partenaires potentiels, avec filtres."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    # Whitelist du champ de tri (sécurité anti-injection SQL)
    sort_whitelist = {"score", "name", "type"}
    if sort not in sort_whitelist:
        raise HTTPException(
            status_code=400,
            detail=f"Tri invalide. Valeurs autorisées: {', '.join(sorted(sort_whitelist))}"
        )

    # Whitelist du type de partenaire
    type_whitelist = {"association", "company", "public"}
    if type and type not in type_whitelist:
        raise HTTPException(
            status_code=400,
            detail=f"Type invalide. Valeurs autorisées: {', '.join(sorted(type_whitelist))}"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Construction de la clause WHERE
    where_clauses = ["1=1"]
    params = []

    if commune:
        where_clauses.append("c.commune = ?")
        params.append(commune)

    if theme:
        where_clauses.append("p.theme_id = ?")
        params.append(theme)

    if type:
        where_clauses.append("p.type = ?")
        params.append(type)

    if search:
        where_clauses.append("(p.name LIKE ? OR c.name LIKE ? OR p.description LIKE ?)")
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])

    where_sql = " AND ".join(where_clauses)

    # Requête COUNT pour le total (pagination)
    count_query = f"""
        SELECT COUNT(*)
        FROM partners p
        LEFT JOIN clubs c ON p.club_id = c.id
        WHERE {where_sql}
    """
    cur.execute(count_query, params)
    total = cur.fetchone()[0]

    # Construction ORDER BY selon paramètre sort
    sort_mapping = {
        "score": "p.score DESC",
        "name": "p.name ASC",
        "type": "p.type ASC, p.score DESC"
    }
    order_sql = sort_mapping[sort]

    # Requête paginée
    offset = (page - 1) * page_size
    query = f"""
        SELECT p.*, c.name as club_name, c.commune
        FROM partners p
        LEFT JOIN clubs c ON p.club_id = c.id
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])

    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    # Calcul du nombre de pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return {
        "shortlist": rows,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "filters_applied": {
            "commune": commune,
            "theme": theme,
            "type": type,
            "search": search,
            "sort": sort
        }
    }


@app.get("/api/shortlist/pdf")
async def get_shortlist_pdf(
    commune: Optional[str] = None,
    theme: Optional[int] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    max_results: int = Query(50, ge=1, le=200, description="Nombre max de partenaires dans le PDF")
):
    """
    Génère un PDF de la shortlist (paysage A4).
    Accepte les mêmes filtres que /api/shortlist.
    """
    from fastapi.responses import Response

    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    # Validation type
    type_whitelist = {"association", "company", "public"}
    if type and type not in type_whitelist:
        raise HTTPException(
            status_code=400,
            detail=f"Type invalide. Valeurs autorisées: {', '.join(sorted(type_whitelist))}"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Construction de la clause WHERE (identique à /api/shortlist)
    where_clauses = ["1=1"]
    params = []

    if commune:
        where_clauses.append("c.commune = ?")
        params.append(commune)

    if theme:
        where_clauses.append("p.theme_id = ?")
        params.append(theme)

    if type:
        where_clauses.append("p.type = ?")
        params.append(type)

    if search:
        where_clauses.append("(p.name LIKE ? OR c.name LIKE ? OR p.description LIKE ?)")
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])

    where_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT p.*, c.name as club_name, c.commune
        FROM partners p
        LEFT JOIN clubs c ON p.club_id = c.id
        WHERE {where_sql}
        ORDER BY p.score DESC
        LIMIT ?
    """
    params.append(max_results)

    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    # Préparer les filtres pour le PDF
    filters = {
        "commune": commune,
        "theme": theme,
        "theme_label": get_theme_label(theme) if theme else "",
        "type": type,
        "search": search,
    }

    commune_label = commune.capitalize() if commune else None

    pdf_bytes = generate_shortlist_pdf(rows, filters, commune_label)

    # Nom de fichier téléchargeable
    today = datetime.now().strftime("%Y%m%d")
    commune_part = f"_{commune}" if commune else ""
    filename = f"territoire-sport_shortlist{commune_part}_{today}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        }
    )


# ════════════════════════════════════════════════════════════════
# Auth API — Endpoints de gestion des tokens partenaires
# ════════════════════════════════════════════════════════════════

@app.post("/api/auth/token")
async def create_partner_token(
    client_name: str = Query(..., description="Nom du client (ex: SM Caen, FC Rouen)"),
    client_email: str = Query(None, description="Email du contact"),
    quota: int = Query(1000, ge=1, le=100000, description="Quota journalier de requêtes"),
    _: dict = Depends(verify_token)  # Seul l'admin peut créer des tokens
):
    """
    Crée un nouveau token partenaire (admin seulement).
    Le token est renvoyé EN CLAIR UNE SEULE FOIS — à transmettre immédiatement au client.
    """
    if _["type"] != "admin":
        raise HTTPException(status_code=403, detail="Seul l'admin peut créer des tokens")

    token = generate_partner_token(client_name, client_email, quota)
    return {
        "token": token,
        "client_name": client_name,
        "client_email": client_email,
        "quota_per_day": quota,
        "warning": "Ce token ne sera plus jamais affiché. Copiez-le maintenant."
    }


@app.get("/api/auth/whoami", dependencies=[Depends(verify_token)])
async def whoami(auth: dict = Depends(verify_token)):
    """
    Retourne les informations d'identité du token utilisé.
    Utile pour les partenaires qui veulent vérifier leur statut et quota restant.
    """
    return {
        "client_name": auth.get("client_name"),
        "type": auth.get("type"),
        "quota_per_day": auth.get("quota_per_day"),
        "used_today": auth.get("used_today", 0),
        "remaining_today": (
            auth.get("quota_per_day", 0) - auth.get("used_today", 0)
            if auth.get("type") == "partner" else "illimité"
        )
    }


@app.get("/api/admin/usage", dependencies=[Depends(verify_token)])
async def usage_stats(_: dict = Depends(verify_token)):
    """
    Statistiques d'usage de l'API par token (admin seulement).
    """
    if _["type"] != "admin":
        raise HTTPException(status_code=403, detail="Seul l'admin peut voir les stats d'usage")

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                client_name,
                client_email,
                quota_per_day,
                request_count,
                last_used_at,
                is_active
            FROM api_tokens
            ORDER BY request_count DESC
        """)
        tokens = [dict(row) for row in cur.fetchall()]

        # Total requêtes aujourd'hui
        cur.execute(
            "SELECT COUNT(*) FROM api_token_usage WHERE used_at LIKE ?",
            (f"{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}%",)
        )
        total_today = cur.fetchone()[0]

        return {
            "total_requests_today": total_today,
            "active_tokens": len([t for t in tokens if t["is_active"]]),
            "tokens": tokens
        }
    finally:
        conn.close()


@app.get("/api/metrics")
async def metrics():
    """Métriques de l'API."""
    return get_metrics()

@app.get("/api/projects")
async def get_projects(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    club_id: Optional[str] = None,
    theme: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Liste des projets avec filtres."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM projects WHERE 1=1"
    params = []

    if club_id:
        query += " AND club_id = ?"
        params.append(club_id)

    if status:
        query += " AND status = ?"
        params.append(status)

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if theme:
        query += " AND themes LIKE ?"
        params.append(f"%{theme}%")

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]

    # Parse themes JSON
    for row in rows:
        if row.get("themes"):
            try:
                row["themes"] = json.loads(row["themes"])
            except:
                row["themes"] = []

    conn.close()
    return {"projects": rows, "count": len(rows), "limit": limit, "offset": offset}


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Detail d'un projet par ID."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cur.fetchone()

    if not project:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")

    project_dict = dict(project)
    if project_dict.get("themes"):
        try:
            project_dict["themes"] = json.loads(project_dict["themes"])
        except:
            project_dict["themes"] = []

    # Club info
    if project_dict.get("club_id"):
        cur.execute("SELECT id, name, sport, city FROM clubs WHERE id = ?", (project_dict["club_id"],))
        club = cur.fetchone()
        if club:
            project_dict["club"] = dict(club)

    conn.close()
    return project_dict



@app.get("/api/cas-inspirants")
async def get_cas_inspirants(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    section: Optional[str] = None,
    thematique: Optional[str] = None,
    niveau_club: Optional[str] = None,
    budget_max: Optional[int] = None
):
    """Liste des cas inspirants avec filtres."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM cas_inspirants WHERE 1=1"
    params = []

    if section:
        query += " AND section = ?"
        params.append(section)
    if niveau_club:
        query += " AND niveau_club = ?"
        params.append(niveau_club)
    if budget_max is not None:
        query += " AND (budget_reel IS NULL OR budget_reel <= ?)"
        params.append(budget_max)

    query += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = cur.fetchall()

    # Parse JSON fields
    cas_list = []
    for row in rows:
        cas = dict(row)
        cas['thematiques'] = json.loads(cas.get('thematiques') or '[]')
        cas['partenaires'] = json.loads(cas.get('partenaires') or '[]')
        cas_list.append(cas)

    conn.close()
    return {"cas_inspirants": cas_list, "total": len(cas_list)}


@app.get("/api/cas-inspirants/match")
async def match_cas_inspirants(
    commune_code: Optional[str] = None,
    thematiques: Optional[str] = None,  # comma-separated
    budget_max: Optional[int] = None,
    niveau_club: Optional[str] = None,
    limit: int = Query(5, ge=1, le=20)
):
    """
    Scoring de cas inspirants selon 3 critères :
    1. Territoire (urbain/rural/maritime/montagneux)
    2. Partenaires non marchands potentiels
    3. Ampleur vs ressources du club
    """
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM cas_inspirants")
    rows = cur.fetchall()
    conn.close()

    thematiques_list = [t.strip() for t in (thematiques or "").split(",") if t.strip()]

    scored = []
    for row in rows:
        cas = dict(row)
        cas_thematiques = json.loads(cas.get('thematiques') or '[]')
        cas_partenaires = json.loads(cas.get('partenaires') or '[]')

        score = 0
        score_details = {}

        # Critère 1 : Thématiques (max 40 pts)
        if thematiques_list:
            matches = len(set(thematiques_list) & set(cas_thematiques))
            theme_score = min(40, matches * 15)
            score += theme_score
            score_details['thematiques'] = theme_score

        # Critère 2 : Partenaires non marchands (max 30 pts)
        # Plus il y a de partenaires non marchands, plus c'est reproductible
        nb_partenaires = len(cas_partenaires)
        partenaire_score = min(30, nb_partenaires * 10)
        score += partenaire_score
        score_details['partenaires'] = partenaire_score

        # Critère 3 : Ampleur vs ressources (max 30 pts)
        # Budget faible + reproductibilité facile = plus accessible
        budget = cas.get('budget_reel') or 0
        repro = cas.get('reproductibilite') or ''
        if budget <= 1000 and 'facile' in repro:
            ampleur_score = 30
        elif budget <= 5000 and 'moyen' in repro:
            ampleur_score = 20
        elif budget <= 10000:
            ampleur_score = 10
        else:
            ampleur_score = 5
        score += ampleur_score
        score_details['ampleur'] = ampleur_score

        # Bonus niveau club
        if niveau_club and cas.get('niveau_club') == niveau_club:
            score += 10
            score_details['bonus_niveau'] = 10

        cas['score'] = score
        cas['score_details'] = score_details
        cas['thematiques'] = cas_thematiques
        cas['partenaires'] = cas_partenaires
        scored.append(cas)

    # Tri par score décroissant
    scored.sort(key=lambda x: x['score'], reverse=True)

    return {"cas_inspirants": scored[:limit], "total": len(scored)}


@app.get("/api/funding-sources")
async def get_funding_sources(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    theme: Optional[str] = None,
    type: Optional[str] = None
):
    """Liste des sources de financement (AAP, fondations, etc.)."""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=503, detail="Database not initialized")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM funding_sources WHERE 1=1"
    params = []

    if type:
        query += " AND type = ?"
        params.append(type)

    if theme:
        query += " AND themes LIKE ?"
        params.append(f"%{theme}%")

    query += " ORDER BY deadline ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]

    for row in rows:
        if row.get("themes"):
            try:
                row["themes"] = json.loads(row["themes"])
            except:
                row["themes"] = []

    conn.close()
    return {"funding_sources": rows, "count": len(rows), "limit": limit, "offset": offset}




# ── Parcours utilisateur — endpoints interactifs ────────────────

@app.post("/api/clubs/register")
async def register_club(payload: dict):
    """Inscription d'un club sportif avec géocodage auto de la commune."""
    import uuid as _uuid
    from datetime import datetime
    import requests as _requests
    
    name = payload.get("name")
    sport = payload.get("sport")
    commune = payload.get("commune")
    email = payload.get("email")
    departement = payload.get("departement", "")
    niveau = payload.get("niveau", "amateur")
    licencies = payload.get("licencies", 0)
    
    if not all([name, sport, commune, email]):
        raise HTTPException(status_code=400, detail="Champs manquants: name, sport, commune, email")
    
    club_id = str(_uuid.uuid4())
    
    # Géocodage automatique via geo.api.gouv.fr
    latitude = None
    longitude = None
    code_insee = None
    epci_code = None
    epci_name = None
    departement_code = departement
    
    try:
        # Recherche de la commune
        geo_resp = _requests.get(
            f"https://geo.api.gouv.fr/communes",
            params={"nom": commune, "fields": "code,centre,codeDepartement,codeEpci,nomEpci", "limit": 1},
            timeout=5
        )
        if geo_resp.status_code == 200:
            communes = geo_resp.json()
            if communes and len(communes) > 0:
                c = communes[0]
                code_insee = c.get("code")
                centre = c.get("centre", {})
                coords = centre.get("coordinates", [None, None])
                longitude = coords[0]
                latitude = coords[1]
                epci_code = c.get("codeEpci")
                epci_name = c.get("nom")  # L'API renvoie 'nom' pour la commune, pas 'nomEpci'
                if not departement_code:
                    departement_code = c.get("codeDepartement")
    except Exception as e:
        print(f"⚠️  Géocodage échoué pour {commune}: {e}")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clubs (
            id, name, sport, city, commune, contact_email, password_hash, created_at,
            department, niveau, licencies, latitude, longitude,
            code_insee, epci_code, epci_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        club_id, name, sport, commune, commune, email, "demo_hash", datetime.now().isoformat(),
        departement_code, niveau, licencies, latitude, longitude,
        code_insee, epci_code, epci_name
    ))
    conn.commit()
    conn.close()
    




    return {
        "club_id": club_id,
        "name": name,
        "sport": sport,
        "commune": commune,
        "departement": departement_code,
        "niveau": niveau,
        "licencies": licencies,
        "latitude": latitude,
        "longitude": longitude,
        "epci": epci_name,
        "code_insee": code_insee,
        "status": "registered"
    }


@app.get("/api/clubs/{club_id}")
async def get_club(club_id: str):
    """Récupère les informations d'un club."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM clubs WHERE id = ?", (club_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Club non trouvé")
    
    return dict(row)


@app.post("/api/diagnostics")
async def create_diagnostic(payload: dict):
    """Soumettre un diagnostic territorial (20 questions)."""
    import uuid as _uuid
    from datetime import datetime
    
    club_id = payload.get("club_id")
    answers = payload.get("answers", {})  # {question_id: score}
    
    if not club_id or not answers:
        raise HTTPException(status_code=400, detail="club_id et answers requis")
    
    # Calcul du score total
    total_score = sum(int(v) for v in answers.values() if str(v).isdigit())
    
    # Détermination du profil
    if total_score >= 15:
        profile = "engaged"
    elif total_score >= 10:
        profile = "emerging"
    elif total_score >= 5:
        profile = "aware"
    else:
        profile = "novice"
    
    diagnostic_id = str(_uuid.uuid4())
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO diagnostics (id, club_id, score, profile, answers, completed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (diagnostic_id, club_id, total_score, profile, str(answers), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return {
        "diagnostic_id": diagnostic_id,
        "club_id": club_id,
        "score": total_score,
        "profile": profile,
        "max_score": 20,
        "answers": answers,
        "recommendation": {
            "engaged": "Votre club est mature. Concentrez-vous sur des projets structurants avec partenaires institutionnels.",
            "emerging": "Votre club est en progression. Visez des projets pilotes avec 2-3 partenaires locaux.",
            "aware": "Votre club démarre. Commencez par des actions simples avec 1-2 partenaires.",
            "novice": "Votre club est novice. Démarrez par un diagnostic territorial approfondi."
        }.get(profile)
    }


@app.get("/api/diagnostics/{diagnostic_id}")
async def get_diagnostic(diagnostic_id: str):
    """Récupérer un diagnostic par ID."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, club_id, score, profile, answers, completed_at FROM diagnostics WHERE id = ?", (diagnostic_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Diagnostic non trouvé")
    
    return {
        "diagnostic_id": row[0],
        "club_id": row[1],
        "score": row[2],
        "profile": row[3],
        "answers": row[4],
        "created_at": row[5]
    }


@app.post("/api/partners/select")
async def select_partners(payload: dict):
    """Sélectionner des partenaires depuis la shortlist."""
    club_id = payload.get("club_id")
    partner_ids = payload.get("partner_ids", [])
    
    if not club_id or not partner_ids:
        raise HTTPException(status_code=400, detail="club_id et partner_ids requis")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Récupérer les détails des partenaires sélectionnés
    placeholders = ",".join("?" * len(partner_ids))
    cur.execute(f"SELECT id, name, type, city, themes FROM partners WHERE id IN ({placeholders})", partner_ids)
    partners = cur.fetchall()
    conn.close()
    
    return {
        "club_id": club_id,
        "selected_count": len(partners),
        "partners": [
            {"id": p[0], "name": p[1], "type": p[2], "city": p[3], "themes": p[4]}
            for p in partners
        ]
    }


@app.post("/api/projects/customize")
async def customize_project(payload: dict):
    """Customiser un projet de bibliothèque."""
    club_id = payload.get("club_id")
    project_id = payload.get("project_id")
    customizations = payload.get("customizations", {})
    
    if not club_id or not project_id:
        raise HTTPException(status_code=400, detail="club_id et project_id requis")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, themes, budget, status FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    return {
        "project_id": row[0],
        "title": row[1],
        "description": row[2],
        "themes": row[3],
        "budget": row[4],
        "status": row[5],
        "customizations_applied": customizations,
        "next_step": "Sélectionnez les AAP matchants"
    }


@app.post("/api/dossiers/generate")
async def generate_dossier(payload: dict):
    """Générer un dossier de candidature."""
    import uuid as _uuid
    from datetime import datetime
    
    club_id = payload.get("club_id")
    project_id = payload.get("project_id")
    funding_source_ids = payload.get("funding_source_ids", [])
    
    if not club_id or not project_id:
        raise HTTPException(status_code=400, detail="club_id et project_id requis")
    
    dossier_id = str(_uuid.uuid4())
    
    return {
        "dossier_id": dossier_id,
        "club_id": club_id,
        "project_id": project_id,
        "funding_sources": funding_source_ids,
        "status": "generated",
        "download_url": f"/api/dossiers/{dossier_id}/download",
        "created_at": datetime.now().isoformat()
    }


@app.get("/demo", response_class=HTMLResponse)
@app.get("/demo.html", response_class=HTMLResponse)
async def get_demo():
    """Page démo HTML."""
    demo_path = Path("production/demo.html")
    if demo_path.exists():
        return HTMLResponse(content=demo_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Demo not found")


@app.get("/architecture", response_class=HTMLResponse)
async def get_architecture():
    """Page architecture & parcours utilisateur."""
    arch_path = Path("production/architecture.html")
    if arch_path.exists():
        return HTMLResponse(content=arch_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Architecture page not found")


@app.get("/parcours", response_class=HTMLResponse)
async def get_parcours():
    """Page parcours utilisateur interactif."""
    p = Path("production/parcours.html")
    if p.exists():
        return HTMLResponse(content=p.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Parcours page not found")


@app.get("/api/communes/{code}/diagnostic-territorial")
async def get_diagnostic_territorial(code: str):
    """Diagnostic territorial d'une commune : réalités, spécificités, difficultés."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Récupérer la commune
    cur.execute("SELECT * FROM communes WHERE code_insee = ?", (code,))
    commune_row = cur.fetchone()
    if not commune_row:
        raise HTTPException(status_code=404, detail="Commune non trouvée")
    commune = dict(commune_row)
    
    # Récupérer le diagnostic territorial
    cur.execute("SELECT * FROM commune_diagnostics WHERE commune_code = ?", (code,))
    diag_row = cur.fetchone()
    
    if not diag_row:
        # Pas de diagnostic pour cette commune — retourner un diagnostic générique
        return {
            "commune": commune,
            "diagnostic": None,
            "message": "Aucun diagnostic territorial disponible pour cette commune"
        }
    
    diag = dict(diag_row)
    # Décoder le JSON des thématiques
    if diag.get('inclusions_thematiques'):
        try:
            diag['inclusions_thematiques'] = json.loads(diag['inclusions_thematiques'])
        except:
            diag['inclusions_thematiques'] = []
    
    return {
        "commune": commune,
        "diagnostic": diag
    }

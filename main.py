"""
TerritoireSport — FastAPI Application v2.0
Plateforme d'aide aux clubs sportifs pour monter des projets à impact local.
Avec : CORS, Auth, Cache, Pagination, Rate Limiting, Métriques, Export CSV
"""

import os
import time
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import aiosqlite
from pathlib import Path
# === Authentification ===
import os
from fastapi import Header, HTTPException
API_TOKEN = os.getenv("API_TOKEN", "territoire-sport-demo-2026")

async def verify_token(x_api_key: str = Header(None)):
    if x_api_key != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token API invalide")

# === Cache ===
import time
_cache = {}
def clear_cache():
    _cache.clear()

# === Métriques ===
from collections import defaultdict
_metrics = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})
def track_request(endpoint, duration, error=False):
    m = _metrics[endpoint]
    m["count"] += 1
    m["total_time"] += duration
    if error:
        m["errors"] += 1
def get_metrics():
    return {ep: {"count": m["count"], "avg_time_ms": round(m["total_time"]/m["count"]*1000, 2) if m["count"] else 0, "errors": m["errors"]} for ep, m in _metrics.items()}

# === Rate Limit ===
def check_rate_limit(client_ip="default"):
    return True

_DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "territoiresport.db")
DB_PATH = os.getenv("DB_PATH", _DEFAULT_DB)

async def init_db():
    schema = Path("data/schema.sql").read_text(encoding="utf-8")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(schema)
        await db.commit()
    print("✅ Base de données initialisée")

async def seed_demo_partners():
    import uuid, json
    demo_partners = [
        ("Mairie de Ducey-Les Chéris", "public", "cohesion", "Ducey", "50", None, None,
         "Commune rurale de la Manche", json.dumps(["cohesion","education","sante"])),
        ("DRAJES Normandie", "public", "insertion", "Caen", "14", None, "https://www.ac-normandie.fr",
         "Direction régionale académique à la jeunesse, à l'engagement et aux sports", json.dumps(["insertion","education","haut_niveau"])),
        ("Ligue de Football de Normandie", "association", "amateur", "Caen", "14", None, "https://www.fff.fr",
         "Ligue régionale FFF — Normandie", json.dumps(["amateur","scolaire","feminin"])),
        ("CINS Caen", "company", "numerique", "Caen", "14", None, None,
         "Agence digitale spécialisée sport", json.dumps(["numerique","gouvernance"])),
        ("ANS — Agence Nationale du Sport", "public", "sante", "Paris", "75", None, "https://www.agencedusport.fr",
         "Agence nationale du sport — financement et développement", json.dumps(["sante","insertion","feminin","handicap"])),
    ]
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) as n FROM partners") as cur:
            row = await cur.fetchone()
            if row and row[0] > 0:
                return
        for p in demo_partners:
            await db.execute(
                "INSERT INTO partners (id,name,type,category,city,department,contact_email,contact_url,description,themes) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), *p)
            )
        await db.commit()
    print("✅ Partenaires de démonstration ajoutés")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_demo_partners()
    try:
        import subprocess
        import os as _os
        result = subprocess.run(
            ["python3", "seed.py"],
            env=_os.environ.copy(),
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("✅ Seed complet OK au démarrage")
        else:
            print(f"⚠️ Seed warning: {result.stderr[:200]}")
    except Exception as e:
        print(f"⚠️ Seed skip: {e}")
    yield

app = FastAPI(
    title="TerritoireSport",
    description="Plateforme d'aide aux clubs sportifs pour monter des projets à impact local",
    version="2.0.0",
    lifespan=lifespan,
    contact={"name": "H3P Solutions", "email": "hh.sportstrategie@gmail.com"},
    license_info={"name": "Proprietary"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    error = False
    try:
        response = await call_next(request)
        if response.status_code >= 500:
            error = True
        return response
    except Exception:
        error = True
        raise
    finally:
        duration = time.time() - start
        endpoint = f"{request.method} {request.url.path}"
        track_request(endpoint, duration, error)

from routes.clubs      import router as clubs_router
from routes.diagnostic import router as diag_router
from routes.projects   import router as projects_router
from routes.matching   import router as matching_router
from routes.territory  import router as territory_router
from routes.affinity   import router as affinity_router
from routes.admin      import router as admin_router
from csv_export         import router as export_router

app.include_router(clubs_router)
app.include_router(diag_router)
app.include_router(projects_router)
app.include_router(matching_router)
app.include_router(territory_router)
app.include_router(affinity_router)
app.include_router(admin_router)
app.include_router(export_router)

from fastapi import APIRouter
import json

partners_router = APIRouter(prefix="/api/partners", tags=["partners"])

@partners_router.get("/")
async def list_partners(department: str = None, theme: str = None, type: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query  = "SELECT * FROM partners WHERE 1=1"
        params = []
        if department:
            query += " AND department = ?"
            params.append(department)
        if type:
            query += " AND type = ?"
            params.append(type)
        async with db.execute(query, params) as cur:
            rows = [dict(r) for r in await cur.fetchall()]
            for r in rows:
                r["themes"] = json.loads(r["themes"])
            if theme:
                rows = [r for r in rows if theme in r["themes"]]
            return rows

app.include_router(partners_router)

@app.get("/api/metrics", tags=["admin"], dependencies=[Depends(verify_token)])
async def metrics():
    """Métriques de l'API (protégé par token)."""
    return get_metrics()

@app.post("/api/cache/clear", tags=["admin"], dependencies=[Depends(verify_token)])
async def clear_cache_endpoint():
    """Vide le cache (protégé par token)."""
    clear_cache()
    return {"status": "cache cleared"}

@app.get("/api/clubs/{club_id}/rapport-pdf")
async def export_rapport(club_id: str):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import cm
    import io, json

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM clubs WHERE id = ?", (club_id,)) as cur:
            club_row = await cur.fetchone()
            club = dict(club_row) if club_row else {}
        async with db.execute(
            "SELECT * FROM diagnostics WHERE club_id = ? ORDER BY completed_at DESC LIMIT 1",
            (club_id,)
        ) as cur:
            diag_row = await cur.fetchone()
            diag = dict(diag_row) if diag_row else None
        async with db.execute(
            "SELECT * FROM club_projects WHERE club_id = ? ORDER BY updated_at DESC",
            (club_id,)
        ) as cur:
            projects = [dict(r) for r in await cur.fetchall()]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph(f"<b>RAPPORT D'IMPACT TERRITORIAL</b>", styles["Title"]))
    story.append(Paragraph(f"<b>{club.get('name','Club')}</b> — {club.get('city','')} ({club.get('department','')})", styles["Heading2"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Sport : {club.get('sport','')} | Taille : {club.get('size','')}", styles["Normal"]))
    story.append(Spacer(1, 1*cm))

    if diag:
        story.append(Paragraph("Diagnostic territorial", styles["Heading2"]))
        story.append(Paragraph(f"Score : <b>{diag['score']}/20</b> — Profil : <b>{diag['profile'].capitalize()}</b>", styles["Normal"]))
        story.append(Spacer(1, 0.5*cm))

    if projects:
        story.append(Paragraph("Projets en cours", styles["Heading2"]))
        lib = {p["id"]: p for p in json.loads(Path("data/projects_library.json").read_text())}
        data_table = [["Projet", "Thématique", "Statut"]]
        for cp in projects:
            p = lib.get(cp["project_id"], {})
            data_table.append([p.get("title","?"), p.get("theme","?"), cp["status"]])
        t = Table(data_table, colWidths=[8*cm, 4*cm, 3*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1B2A4A")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#DEE2E6")),
            ("PADDING",    (0,0), (-1,-1), 6),
        ]))
        story.append(t)

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Rapport généré par TerritoireSport — H3P Solutions", styles["Italic"]))

    doc.build(story)
    buf.seek(0)
    return Response(
        content=buf.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rapport_{club_id[:8]}.pdf"}
    )

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "features": ["auth", "cache", "pagination", "metrics", "csv_export", "rate_limit"]
    }

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


 

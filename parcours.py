"""
TerritoireSport — Module parcours utilisateur complet
=====================================================
Endpoints pour le flow club → projet → shortlist → contact partenaire → KPIs.

Tables nouvelles :
- club_sessions : token de session des clubs (login)
- partner_contact_requests : demandes de contact envoyées aux partenaires
- partner_responses : acceptation / refus des partenaires

Tables existantes réutilisées :
- clubs : comptes club
- engineering_projects : projets d'ingénierie (workflow étape par étape)
- project_steps : étapes d'un projet
- partners : annuaire des partenaires potentiels
"""
import os
import sqlite3
import secrets
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from pydantic import BaseModel

import json
from db_config import DB_PATH

# ── Mapping thématique : slug ↔ id numérique (cohérent avec /api/themes) ──
THEME_SLUG_TO_ID = {
    "sante": 1, "insertion": 2, "cohesion": 3, "environnement": 4,
    "education": 5, "culture": 6, "economie": 7, "egalite": 8,
    "handicap": 9, "seniors": 10, "prevention": 11, "numerique": 12,
    "gouvernance": 13, "haut_niveau": 14, "feminin": 15, "amateur": 16,
    "scolaire": 17, "mobilite": 18, "tourisme": 19,
}
THEME_ID_TO_SLUG = {v: k for k, v in THEME_SLUG_TO_ID.items()}

router = APIRouter(prefix="/api/parcours", tags=["parcours"])


# ── Schéma des nouvelles tables ─────────────────────────────────────────

PARCOURS_SCHEMA = """
CREATE TABLE IF NOT EXISTS club_sessions (
    token TEXT PRIMARY KEY,
    club_id TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT NOT NULL,
    FOREIGN KEY (club_id) REFERENCES clubs(id)
);

CREATE TABLE IF NOT EXISTS partner_contact_requests (
    id TEXT PRIMARY KEY,
    club_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    partner_id TEXT NOT NULL,
    partner_token TEXT NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (club_id) REFERENCES clubs(id),
    FOREIGN KEY (project_id) REFERENCES engineering_projects(id),
    FOREIGN KEY (partner_id) REFERENCES partners(id)
);

CREATE TABLE IF NOT EXISTS partner_responses (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    partner_token TEXT NOT NULL,
    response TEXT NOT NULL,
    comment TEXT,
    responded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (request_id) REFERENCES partner_contact_requests(id)
);
"""


def init_parcours_tables():
    """Crée les tables nécessaires au parcours utilisateur + corrige les colonnes manquantes."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(PARCOURS_SCHEMA)
    conn.commit()

    # ── Migration douce : ajouter les colonnes manquantes à clubs (legacy init_db.py) ──
    expected_cols = {
        "email": "TEXT",
        "password_hash": "TEXT",
        "members_count": "INTEGER DEFAULT 0",
        "region": "TEXT DEFAULT 'Normandie'",
        "description": "TEXT",
        "website": "TEXT",
        "updated_at": "TEXT",
    }
    existing_cols = [row[1] for row in conn.execute("PRAGMA table_info(clubs)").fetchall()]
    for col, typedef in expected_cols.items():
        if col not in existing_cols:
            try:
                conn.execute(f"ALTER TABLE clubs ADD COLUMN {col} {typedef}")
                conn.commit()
            except Exception:
                pass

    conn.close()


def hash_password(password: str) -> str:
    """Hash simple SHA-256 (suffisant pour démo)."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_db():
    """Helper pour obtenir une connexion DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ════════════════════════════════════════════════════════════════════════
# Modèles Pydantic
# ════════════════════════════════════════════════════════════════════════


class ClubRegister(BaseModel):
    name: str
    email: str
    password: str
    sport: Optional[str] = None
    city: Optional[str] = None
    department: Optional[str] = None
    members_count: Optional[int] = None


class ClubLogin(BaseModel):
    email: str
    password: str


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    theme_id: Optional[str] = None
    public_cible: Optional[str] = None
    objectifs: Optional[str] = None
    activites: Optional[str] = None
    ressources: Optional[str] = None
    calendrier: Optional[str] = None
    indicateurs: Optional[str] = None


class ContactRequest(BaseModel):
    partner_id: str
    message: Optional[str] = None


class PartnerRespond(BaseModel):
    response: str  # "accepted" | "declined"
    comment: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# 1. Inscription club
# ════════════════════════════════════════════════════════════════════════


@router.post("/clubs/register")
async def register_club(club: ClubRegister):
    """
    Étape 1 du parcours : un club s'inscrit sur la plateforme.
    Crée le compte club + retourne les infos de confirmation.
    """
    conn = get_db()
    try:
        # Vérifier si l'email existe déjà
        existing = conn.execute(
            "SELECT id FROM clubs WHERE email = ?", (club.email,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Un club existe déjà avec cet email")

        club_id = f"club-{secrets.token_hex(6)}"
        now = datetime.utcnow().isoformat()

        conn.execute(
            """
            INSERT INTO clubs (id, name, email, password_hash, sport, city, department,
                               members_count, region, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Normandie', ?, ?)
            """,
            (
                club_id, club.name, club.email, hash_password(club.password),
                club.sport, club.city, club.department, club.members_count,
                now, now,
            ),
        )
        conn.commit()

        return {
            "club_id": club_id,
            "name": club.name,
            "email": club.email,
            "message": "🎉 Bienvenue ! Votre compte club est créé. Connectez-vous pour démarrer votre projet.",
            "next_step": "POST /api/parcours/clubs/login",
        }
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════
# 2. Connexion club
# ════════════════════════════════════════════════════════════════════════


@router.post("/clubs/login")
async def login_club(credentials: ClubLogin):
    """
    Étape 3 du parcours : un club se connecte.
    Retourne un token de session club (valable 7 jours).
    """
    conn = get_db()
    try:
        club = conn.execute(
            "SELECT id, name, email, password_hash FROM clubs WHERE email = ?",
            (credentials.email,),
        ).fetchone()

        if not club:
            raise HTTPException(status_code=404, detail="Aucun club avec cet email. Inscrivez-vous d'abord.")

        if club["password_hash"] != hash_password(credentials.password):
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")

        # Générer token de session (valable 7 jours)
        session_token = f"club-session-{secrets.token_urlsafe(24)}"
        now = datetime.utcnow()
        expires = datetime.utcnow().replace(
            day=now.day + 7 if now.day <= 24 else now.day - 24 + 7
        )
        # Version safe : ajouter 7 jours
        from datetime import timedelta
        expires = (now + timedelta(days=7)).isoformat()

        conn.execute(
            """
            INSERT INTO club_sessions (token, club_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_token, club["id"], now.isoformat(), expires),
        )
        conn.commit()

        return {
            "club_token": session_token,
            "club_id": club["id"],
            "name": club["name"],
            "expires_at": expires,
            "message": f"👋 Bienvenue {club['name']} ! Vous pouvez maintenant créer votre projet.",
            "next_step": "POST /api/parcours/projects",
        }
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════
# 3. Création de projet d'ingénierie
# ════════════════════════════════════════════════════════════════════════


async def verify_club_token(authorization: Optional[str] = Header(None)):
    """Vérifie le token club (header Authorization: Bearer <token>)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token club manquant. Format: 'Authorization: Bearer <token>'")
    token = authorization.replace("Bearer ", "")
    conn = get_db()
    try:
        session = conn.execute(
            "SELECT club_id, expires_at FROM club_sessions WHERE token = ?", (token,)
        ).fetchone()
        if not session:
            raise HTTPException(status_code=401, detail="Token invalide")
        # Vérifier expiration
        if datetime.fromisoformat(session["expires_at"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expiré. Reconnectez-vous.")
        return session["club_id"]
    finally:
        conn.close()


@router.post("/projects")
async def create_project(
    project: ProjectCreate,
    club_id: str = Depends(verify_club_token),
):
    """
    Étape 4 du parcours : un club crée son projet sociétal.
    Initialise automatiquement les 5 étapes du workflow.
    """
    conn = get_db()
    try:
        project_id = f"proj-{secrets.token_hex(6)}"
        now = datetime.utcnow().isoformat()

        conn.execute(
            """
            INSERT INTO engineering_projects (
                id, club_id, theme_id, public_cible, objectifs, activites,
                ressources, calendrier, indicateurs, status, current_step,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', 1, ?, ?)
            """,
            (
                project_id, club_id, project.theme_id, project.public_cible,
                project.objectifs, project.activites, project.ressources,
                project.calendrier, project.indicateurs, now, now,
            ),
        )

        # Créer les 5 étapes du workflow
        steps = [
            (1, "Diagnostic territorial", False),
            (2, "Identification partenaires", False),
            (3, "Construction dossier AAP", False),
            (4, "Mise en relation terrain", False),
            (5, "Bilan & mesure impact", False),
        ]
        for step_num, step_name, completed in steps:
            step_id = f"step-{secrets.token_hex(4)}"
            conn.execute(
                """
                INSERT INTO project_steps (id, project_id, step_number, step_name, completed, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (step_id, project_id, step_num, step_name, completed,
                 now if completed else None),
            )

        conn.commit()

        return {
            "project_id": project_id,
            "title": project.title,
            "status": "active",
            "current_step": 1,
            "steps": [{"number": n, "name": name, "completed": False} for n, name, _ in steps],
            "message": "✨ Projet créé ! Étape 1 : diagnostic territorial.",
            "next_step": "GET /api/parcours/shortlist?project_id=...",
        }
    finally:
        conn.close()


@router.get("/projects/{project_id}")
async def get_project(project_id: str, club_id: str = Depends(verify_club_token)):
    """Récupère un projet et l'état de ses étapes."""
    conn = get_db()
    try:
        project = conn.execute(
            "SELECT * FROM engineering_projects WHERE id = ? AND club_id = ?",
            (project_id, club_id),
        ).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        steps = conn.execute(
            "SELECT step_number, step_name, completed, completed_at FROM project_steps WHERE project_id = ? ORDER BY step_number",
            (project_id,),
        ).fetchall()

        return {
            "project": dict(project),
            "steps": [dict(s) for s in steps],
            "completion_percent": sum(1 for s in steps if s["completed"]) / len(steps) * 100,
        }
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════
# 4. Shortlist filtrée par projet
# ════════════════════════════════════════════════════════════════════════


@router.get("/shortlist")
async def get_parcours_shortlist(
    project_id: str,
    theme: Optional[int] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    club_id: str = Depends(verify_club_token),
):
    """
    Étape 5 du parcours : shortlist personnalisée pour le projet du club.
    Filtre les partenaires selon le thème du projet et la commune du club.
    """
    conn = get_db()
    try:
        # Récupérer projet + club pour contexte
        project = conn.execute(
            "SELECT * FROM engineering_projects WHERE id = ? AND club_id = ?",
            (project_id, club_id),
        ).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        club = conn.execute(
            "SELECT city, department FROM clubs WHERE id = ?", (club_id,)
        ).fetchone()

        # Construire la requête
        query = "SELECT * FROM partners WHERE 1=1"
        params = []

        # Filtre thème (utilise le theme_id du projet par défaut)
        # Conversion: theme_id du projet peut être soit un slug textuel, soit un id numérique
        theme_value = theme or project["theme_id"]
        if theme_value:
            # Si c'est un id numérique, convertir en slug
            if isinstance(theme_value, str) and theme_value.isdigit():
                effective_theme_slug = THEME_ID_TO_SLUG.get(int(theme_value), theme_value)
            else:
                effective_theme_slug = theme_value  # déjà un slug
            # Filtre sur themes contient le slug
            query += " AND themes LIKE ?"
            params.append(f"%\"{effective_theme_slug}\"%")
        else:
            effective_theme_slug = None

        if type:
            query += " AND type = ?"
            params.append(type)

        if search:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        # Filtre géographique bonus (partenaires dans le même département)
        if club and club["department"]:
            query += " AND (department = ? OR department IS NULL)"
            params.append(club["department"])

        # Compter le total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        total = conn.execute(count_query, params).fetchone()[0]

        # Paginer
        offset = (page - 1) * page_size
        query += " ORDER BY name LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        rows = conn.execute(query, params).fetchall()
        partners = []
        for row in rows:
            p = dict(row)
            # Calculer un score simple (juste pour la démo)
            score = 50
            if effective_theme_slug and effective_theme_slug in (p.get("themes") or ""):
                score += 30
            if club and p.get("department") == club["department"]:
                score += 20
            p["score"] = min(score, 100)
            partners.append(p)

        total_pages = (total + page_size - 1) // page_size

        return {
            "project_id": project_id,
            "partners": partners,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
            "filters_applied": {
                "theme": effective_theme_slug,
                "type": type,
                "search": search,
                "department": club["department"] if club else None,
            },
        }
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════
# 5. Initier un contact (génère un token partageable pour le partenaire)
# ════════════════════════════════════════════════════════════════════════


@router.post("/projects/{project_id}/contact")
async def initiate_contact(
    project_id: str,
    contact: ContactRequest,
    club_id: str = Depends(verify_club_token),
):
    """
    Étape 8 du parcours : le club initie un contact avec un partenaire.
    Génère un token unique que le partenaire utilisera pour répondre.
    """
    conn = get_db()
    try:
        # Vérifier que le projet appartient au club
        project = conn.execute(
            "SELECT title FROM engineering_projects WHERE id = ? AND club_id = ?",
            (project_id, club_id),
        ).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        # Vérifier que le partenaire existe
        partner = conn.execute(
            "SELECT id, name FROM partners WHERE id = ?", (contact.partner_id,)
        ).fetchone()
        if not partner:
            raise HTTPException(status_code=404, detail="Partenaire non trouvé")

        # Générer token de réponse partenaire
        request_id = f"contact-{secrets.token_hex(6)}"
        partner_token = secrets.token_urlsafe(20)

        conn.execute(
            """
            INSERT INTO partner_contact_requests (
                id, club_id, project_id, partner_id, partner_token, message, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (
                request_id, club_id, project_id, contact.partner_id,
                partner_token, contact.message, datetime.utcnow().isoformat(),
            ),
        )

        # Marquer l'étape 4 comme "en cours"
        conn.execute(
            "UPDATE project_steps SET completed = 0 WHERE project_id = ? AND step_number = 4",
            (project_id,),
        )
        conn.execute(
            "UPDATE engineering_projects SET current_step = 4, updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), project_id),
        )

        conn.commit()

        # Construire l'URL que le partenaire ouvrira
        partner_url = f"/parcours/partenaire?token={partner_token}"

        return {
            "request_id": request_id,
            "partner_token": partner_token,
            "partner_url": partner_url,
            "partner_name": partner["name"],
            "project_title": project["title"],
            "message": f"📨 Demande envoyée à {partner['name']}. Ils ont 7 jours pour répondre.",
            "next_step": "Attendre la réponse du partenaire (notification simulée en haut de page)",
        }
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════
# 6. Partenaire consulte et répond (sans auth, juste token)
# ════════════════════════════════════════════════════════════════════════


@router.get("/partenaire/inbox")
async def partenaire_inbox(token: str = Query(...)):
    """
    Le partenaire accède à sa boîte de réception via son token.
    """
    conn = get_db()
    try:
        # Récupérer la demande via token
        request = conn.execute(
            """
            SELECT pcr.*, c.name as club_name, ep.title as project_title,
                   ep.description as project_description, ep.theme_id,
                   p.name as partner_name, p.contact_email
            FROM partner_contact_requests pcr
            JOIN clubs c ON c.id = pcr.club_id
            JOIN engineering_projects ep ON ep.id = pcr.project_id
            JOIN partners p ON p.id = pcr.partner_id
            WHERE pcr.partner_token = ?
            """,
            (token,),
        ).fetchone()
        if not request:
            raise HTTPException(status_code=404, detail="Token invalide ou expiré")

        # Récupérer la réponse existante
        existing_response = conn.execute(
            "SELECT * FROM partner_responses WHERE partner_token = ?", (token,)
        ).fetchone()

        return {
            "request": dict(request),
            "existing_response": dict(existing_response) if existing_response else None,
            "action": "POST /api/parcours/partenaire/respond",
        }
    finally:
        conn.close()


@router.post("/partenaire/respond")
async def partenaire_respond(token: str, response: PartnerRespond):
    """
    Le partenaire accepte ou refuse la demande de contact.
    """
    if response.response not in ("accepted", "declined"):
        raise HTTPException(status_code=400, detail="response doit être 'accepted' ou 'declined'")

    conn = get_db()
    try:
        # Vérifier que la demande existe
        request = conn.execute(
            "SELECT id, status FROM partner_contact_requests WHERE partner_token = ?",
            (token,),
        ).fetchone()
        if not request:
            raise HTTPException(status_code=404, detail="Token invalide")
        if request["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Cette demande a déjà reçu une réponse ({request['status']})")

        # Enregistrer la réponse
        response_id = f"resp-{secrets.token_hex(6)}"
        conn.execute(
            """
            INSERT INTO partner_responses (id, request_id, partner_token, response, comment, responded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (response_id, request["id"], token, response.response, response.comment,
             datetime.utcnow().isoformat()),
        )

        # Mettre à jour le statut de la demande
        conn.execute(
            "UPDATE partner_contact_requests SET status = ? WHERE id = ?",
            (response.response, request["id"]),
        )

        # Si accepté, marquer l'étape 4 comme complétée + passer à étape 5
        if response.response == "accepted":
            conn.execute(
                "UPDATE project_steps SET completed = 1, completed_at = ? WHERE project_id = (SELECT project_id FROM partner_contact_requests WHERE id = ?) AND step_number = 4",
                (datetime.utcnow().isoformat(), request["id"]),
            )
            conn.execute(
                """UPDATE engineering_projects
                   SET current_step = 5, updated_at = ?
                   WHERE id = (SELECT project_id FROM partner_contact_requests WHERE id = ?)""",
                (datetime.utcnow().isoformat(), request["id"]),
            )

        conn.commit()

        return {
            "response_id": response_id,
            "request_id": request["id"],
            "response": response.response,
            "message": (
                f"✅ Vous avez accepté la demande de contact. Le club en sera informé."
                if response.response == "accepted"
                else f"❌ Vous avez refusé la demande. Le club en sera informé."
            ),
        }
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════
# 7. KPIs admin — dashboard temps réel
# ════════════════════════════════════════════════════════════════════════


@router.get("/admin/conversion-stats")
async def conversion_stats():
    """
    KPIs temps réel du parcours utilisateur.
    Pas d'auth pour démo, à protéger en prod avec verify_token.
    """
    conn = get_db()
    try:
        # Clubs inscrits
        total_clubs = conn.execute("SELECT COUNT(*) FROM clubs").fetchone()[0]

        # Sessions actives (7 derniers jours)
        active_sessions = conn.execute(
            "SELECT COUNT(*) FROM club_sessions WHERE expires_at > datetime('now')"
        ).fetchone()[0]

        # Projets créés
        total_projects = conn.execute("SELECT COUNT(*) FROM engineering_projects").fetchone()[0]

        # Projets par étape
        projects_by_step = conn.execute(
            "SELECT current_step, COUNT(*) as count FROM engineering_projects GROUP BY current_step"
        ).fetchall()

        # Demandes de contact envoyées
        total_requests = conn.execute("SELECT COUNT(*) FROM partner_contact_requests").fetchone()[0]
        pending_requests = conn.execute("SELECT COUNT(*) FROM partner_contact_requests WHERE status = 'pending'").fetchone()[0]
        accepted_requests = conn.execute("SELECT COUNT(*) FROM partner_contact_requests WHERE status = 'accepted'").fetchone()[0]
        declined_requests = conn.execute("SELECT COUNT(*) FROM partner_contact_requests WHERE status = 'declined'").fetchone()[0]

        # Taux de conversion étape par étape
        conversion_rate = (
            round(accepted_requests / total_requests * 100, 1) if total_requests > 0 else 0
        )

        return {
            "clubs": {
                "total_inscrits": total_clubs,
                "sessions_actives": active_sessions,
            },
            "projects": {
                "total": total_projects,
                "by_step": {row["current_step"]: row["count"] for row in projects_by_step},
            },
            "contact_requests": {
                "total_envoyees": total_requests,
                "pending": pending_requests,
                "accepted": accepted_requests,
                "declined": declined_requests,
                "taux_acceptation": conversion_rate,
            },
            "funnel": [
                {"etape": "1. Inscription club", "count": total_clubs},
                {"etape": "2. Création projet", "count": total_projects},
                {"etape": "3. Contact partenaire", "count": total_requests},
                {"etape": "4. Partenaire accepté", "count": accepted_requests},
            ],
        }
    finally:
        conn.close()

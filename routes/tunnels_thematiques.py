"""
Routes API pour les 3 tunnels thématiques.

Endpoints :
- /api/tunnels/list                       → Liste des 3 tunnels
- /api/tunnels/{slug}                     → Détail d'un tunnel (étapes)
- /api/tunnels/routage/questions          → Questions pour orienter le club
- /api/tunnels/routage/calculer           → Calcule le tunnel recommandé selon profil
- /api/tunnels/projets/{id}/choisir       → Choisit le tunnel pour un projet
- /api/tunnels/projets/{id}/tunnel        → Tunnel associé à un projet
"""

from fastapi import APIRouter, HTTPException
from db_config import DB_PATH
import aiosqlite
import uuid
import json
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/api/tunnels", tags=["tunnels-thematiques"])


def load_tunnels_data():
    """Charge les données des tunnels thématiques."""
    base = Path("data/ingenierie_projet")
    return {
        "tunnels": json.loads((base / "tunnels_thematiques.json").read_text(encoding="utf-8")),
        "routage": json.loads((base / "routage_tunnel.json").read_text(encoding="utf-8")),
    }


# ── Liste des tunnels ─────────────────────────────────────────────

@router.get("/list")
async def list_tunnels():
    """Retourne la liste des 3 tunnels thématiques avec leur description."""
    data = load_tunnels_data()
    tunnels = []
    for slug, tunnel in data["tunnels"]["tunnels"].items():
        tunnels.append({
            "slug": slug,
            "name": tunnel["name"],
            "icon": tunnel["icon"],
            "couleur": tunnel["couleur"],
            "description": tunnel["description"],
            "public_cible": tunnel["public_cible"],
            "duree_estimation_totale": tunnel["duree_estimation_totale"],
            "nb_etapes": tunnel["nb_etapes"],
        })
    return {"tunnels": tunnels}


# ── Détail d'un tunnel ─────────────────────────────────────────────

@router.get("/{slug}")
async def get_tunnel(slug: str):
    """Retourne le détail d'un tunnel (toutes les étapes)."""
    data = load_tunnels_data()
    tunnel = data["tunnels"]["tunnels"].get(slug)
    if not tunnel:
        raise HTTPException(404, f"Tunnel '{slug}' non trouvé")
    return tunnel


# ── Questions de routage ───────────────────────────────────────────

@router.get("/routage/questions")
async def get_routage_questions():
    """Retourne les questions pour orienter un club vers le bon tunnel."""
    data = load_tunnels_data()
    return {
        "questions": data["routage"]["questions"],
        "regle": data["routage"]["regle_routage"],
    }


# ── Calcul du tunnel recommandé ────────────────────────────────────

@router.post("/routage/calculer")
async def calculate_tunnel_routage(payload: dict):
    """
    Calcule le tunnel recommandé selon les réponses au questionnaire de routage.

    Body : { "club_id": "...", "reponses": { "nature_projet": 1, "nb_partenaires": 2, ... } }
    """
    tunnel_data = load_tunnels_data()
    questions = tunnel_data["routage"]["questions"]
    mapping = tunnel_data["routage"]["regle_routage"]["mapping"]

    reponses = payload.get("reponses", {})
    club_id = payload.get("club_id")

    if not club_id:
        raise HTTPException(400, "club_id requis")

    # Vérifier que toutes les questions ont une réponse
    for q in questions:
        if q["slug"] not in reponses:
            raise HTTPException(400, f"Réponse manquante pour : {q['slug']}")

    # Calculer le score total
    score_total = sum(int(reponses[q["slug"]]) for q in questions)

    # Déterminer le tunnel recommandé
    tunnel_recommande = "action_directe"  # défaut
    raison = "Score par défaut"
    for m in mapping:
        if m["score_min"] <= score_total <= m["score_max"]:
            tunnel_recommande = m["tunnel"]
            raison = m["raison"]
            break

    # Récupérer les détails du tunnel recommandé
    tunnel_info = tunnel_data["tunnels"]["tunnels"][tunnel_recommande]

    # Sauvegarder en BDD
    routage_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS tunnel_routages (
                id TEXT PRIMARY KEY,
                club_id TEXT NOT NULL,
                reponses TEXT NOT NULL,
                score_total INTEGER NOT NULL,
                tunnel_recommande TEXT NOT NULL,
                raison TEXT,
                created_at TEXT NOT NULL
            )"""
        )
        await db.execute(
            "INSERT INTO tunnel_routages (id, club_id, reponses, score_total, tunnel_recommande, raison, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (routage_id, club_id, json.dumps(reponses), score_total, tunnel_recommande, raison, now)
        )
        await db.commit()

    return {
        "id": routage_id,
        "club_id": club_id,
        "score_total": score_total,
        "tunnel_recommande": tunnel_recommande,
        "tunnel_info": {
            "name": tunnel_info["name"],
            "icon": tunnel_info["icon"],
            "couleur": tunnel_info["couleur"],
            "description": tunnel_info["description"],
            "nb_etapes": tunnel_info["nb_etapes"],
            "duree_estimation_totale": tunnel_info["duree_estimation_totale"],
        },
        "raison": raison,
        "alternatives": [
            m["tunnel"] for m in mapping
            if m["tunnel"] != tunnel_recommande
        ],
        "created_at": now,
    }


# ── Choisir un tunnel pour un projet ───────────────────────────────

@router.post("/projets/{projet_id}/choisir")
async def choisir_tunnel_projet(projet_id: str, payload: dict):
    """
    Associe un tunnel thématique à un projet en construction.

    Body : { "club_id": "...", "tunnel_slug": "action_directe" }
    """
    tunnel_data = load_tunnels_data()
    tunnel_slug = payload.get("tunnel_slug")
    if not tunnel_slug or tunnel_slug not in tunnel_data["tunnels"]["tunnels"]:
        raise HTTPException(400, f"Tunnel '{tunnel_slug}' invalide")
    tunnel = tunnel_data["tunnels"]["tunnels"][tunnel_slug]

    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        # Vérifier que le projet existe
        async with db.execute("SELECT id FROM tunnel_projets WHERE id = ?", (projet_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                raise HTTPException(404, "Projet non trouvé")

        # S'assurer que la colonne tunnel_slug existe (migration safe)
        async with db.execute("PRAGMA table_info(tunnel_projets)") as cur:
            cols = [c[1] for c in await cur.fetchall()]
        if "tunnel_slug" not in cols:
            await db.execute("ALTER TABLE tunnel_projets ADD COLUMN tunnel_slug TEXT")

        await db.execute(
            "UPDATE tunnel_projets SET tunnel_slug = ?, updated_at = ? WHERE id = ?",
            (tunnel_slug, now, projet_id)
        )
        await db.commit()

    return {
        "projet_id": projet_id,
        "tunnel_slug": tunnel_slug,
        "tunnel_name": tunnel["name"],
        "nb_etapes": tunnel["nb_etapes"],
        "updated_at": now,
    }


# ── Récupérer le tunnel d'un projet ────────────────────────────────

@router.get("/projets/{projet_id}/tunnel")
async def get_projet_tunnel(projet_id: str):
    """Récupère le tunnel associé à un projet."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT tunnel_slug FROM tunnel_projets WHERE id = ?", (projet_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                raise HTTPException(404, "Projet non trouvé")
            tunnel_slug = row["tunnel_slug"] or "action_directe"

    tunnel_data = load_tunnels_data()
    tunnel = tunnel_data["tunnels"]["tunnels"].get(
        tunnel_slug, tunnel_data["tunnels"]["tunnels"]["action_directe"]
    )
    return tunnel
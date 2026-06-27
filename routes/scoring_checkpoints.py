"""
Routes API pour les scoring checkpoints par étape.

Endpoints :
- /api/scoring/checkpoints/{projet_id}/{etape_numero}  → Calcule le score d'un checkpoint
"""

from fastapi import APIRouter, HTTPException
import aiosqlite
from db_config import DB_PATH
from pathlib import Path
import json

router = APIRouter(prefix="/api/scoring", tags=["scoring-checkpoints"])


def load_tunnels_data():
    """Charge les données des tunnels thématiques."""
    base = Path("data/ingenierie_projet")
    return {
        "tunnels": json.loads((base / "tunnels_thematiques.json").read_text(encoding="utf-8")),
        "scoring": json.loads((base / "scoring_faisabilite.json").read_text(encoding="utf-8")),
    }


@router.post("/checkpoints/{projet_id}/{etape_numero}")
async def calculate_checkpoint(projet_id: str, etape_numero: int, data: dict):
    """
    Calcule le score d'un checkpoint pour une étape donnée.

    Body : { "club_id": "...", "scores": { "critere_id": 0-10, ... } }

    Retourne : score du checkpoint, niveau, recommandation
    """
    tunnel_data = load_tunnels_data()

    # Récupérer le tunnel du projet
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT tunnel_slug FROM tunnel_projets WHERE id = ?", (projet_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                raise HTTPException(404, "Projet non trouvé")
            tunnel_slug = row["tunnel_slug"] or "action_directe"

    tunnel = tunnel_data["tunnels"]["tunnels"].get(tunnel_slug)
    if not tunnel:
        raise HTTPException(404, f"Tunnel '{tunnel_slug}' non trouvé")

    # Trouver l'étape
    etape = next((e for e in tunnel["etapes"] if e["numero"] == etape_numero), None)
    if not etape:
        raise HTTPException(404, f"Étape {etape_numero} non trouvée dans tunnel {tunnel_slug}")

    # Récupérer les critères du checkpoint
    criteres_ids = etape.get("scoring_checkpoint", [])
    if not criteres_ids:
        raise HTTPException(400, "Aucun critère de checkpoint pour cette étape")

    # Récupérer les détails des critères
    all_criteres = tunnel_data["scoring"]["criteres"]
    criteres_details = [c for c in all_criteres if c["slug"] in criteres_ids]

    # Calculer le score
    scores_provided = data.get("scores", {})
    score_total = 0
    score_max = len(criteres_details) * 10
    details = []

    for critere in criteres_details:
        score = scores_provided.get(critere["slug"], 0)
        score_total += score
        details.append({
            "id": critere["slug"],
            "nom": critere["titre"],
            "score": score,
            "max": 10,
        })

    # Déterminer le niveau
    pourcentage = (score_total / score_max * 100) if score_max > 0 else 0
    if pourcentage >= 75:
        niveau = "très_favorable"
        recommandation = "✅ Vous pouvez passer à l'étape suivante en confiance."
    elif pourcentage >= 50:
        niveau = "favorable"
        recommandation = "👍 Vous pouvez continuer, mais identifiez les points à renforcer."
    elif pourcentage >= 25:
        niveau = "à_renforcer"
        recommandation = "⚠️ Prenez le temps de consolider les points faibles avant de continuer."
    else:
        niveau = "bloquant"
        recommandation = "🛑 Ce checkpoint est bloquant. Revoyez les fondamentaux avant de continuer."

    # Sauvegarder en BDD
    import uuid
    from datetime import datetime
    checkpoint_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS tunnel_checkpoints (
                id TEXT PRIMARY KEY,
                projet_id TEXT NOT NULL,
                etape_numero INTEGER NOT NULL,
                scores TEXT NOT NULL,
                score_total INTEGER NOT NULL,
                score_max INTEGER NOT NULL,
                niveau TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        await db.execute(
            "INSERT INTO tunnel_checkpoints (id, projet_id, etape_numero, scores, score_total, score_max, niveau, created_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (checkpoint_id, projet_id, etape_numero, json.dumps(scores_provided), score_total, score_max, niveau, now)
        )
        await db.commit()

    return {
        "id": checkpoint_id,
        "projet_id": projet_id,
        "etape_numero": etape_numero,
        "etape_titre": etape["titre"],
        "score_total": score_total,
        "score_max": score_max,
        "pourcentage": round(pourcentage, 1),
        "niveau": niveau,
        "recommandation": recommandation,
        "details": details,
        "created_at": now,
    }


@router.get("/checkpoints/{projet_id}/{etape_numero}")
async def get_checkpoint(projet_id: str, etape_numero: int):
    """Récupère le dernier checkpoint d'une étape."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tunnel_checkpoints WHERE projet_id = ? AND etape_numero = ? ORDER BY created_at DESC LIMIT 1",
            (projet_id, etape_numero)
        ) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "projet_id": row["projet_id"],
                "etape_numero": row["etape_numero"],
                "score_total": row["score_total"],
                "score_max": row["score_max"],
                "pourcentage": round(row["score_total"] / row["score_max"] * 100, 1),
                "niveau": row["niveau"],
                "scores": json.loads(row["scores"]),
                "created_at": row["created_at"],
            }


@router.get("/checkpoints/{projet_id}")
async def list_checkpoints(projet_id: str):
    """Liste tous les checkpoints d'un projet."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tunnel_checkpoints WHERE projet_id = ? ORDER BY etape_numero, created_at DESC",
            (projet_id,)
        ) as cur:
            rows = await cur.fetchall()
            return [
                {
                    "id": row["id"],
                    "etape_numero": row["etape_numero"],
                    "score_total": row["score_total"],
                    "score_max": row["score_max"],
                    "pourcentage": round(row["score_total"] / row["score_max"] * 100, 1),
                    "niveau": row["niveau"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
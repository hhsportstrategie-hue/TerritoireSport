from fastapi import APIRouter, HTTPException
from db_config import DB_PATH
import json
from pathlib import Path
from models.diagnostic import PROFILES, compute_profile

router = APIRouter(prefix="/api/matching", tags=["matching"])

def load_library():
    return json.loads(Path("data/projects_library.json").read_text(encoding="utf-8"))

@router.get("/{club_id}")
async def match_projects(club_id: str, limit: int = 5):
    """
    Algorithme de matching : retourne les projets les plus adaptés au profil du club.
    Score de compatibilité basé sur :
    - Profil du diagnostic (difficulty)
    - Sport du club (certains projets sont sport-spécifiques)
    - Taille du club (budget)
    """
    import aiosqlite
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Récupérer le club
        async with db.execute("SELECT * FROM clubs WHERE id = ?", (club_id,)) as cur:
            club = await cur.fetchone()
            if not club:
                raise HTTPException(404, "Club non trouvé")
            club = dict(club)

        # Récupérer le dernier diagnostic
        async with db.execute(
            "SELECT * FROM diagnostics WHERE club_id = ? ORDER BY completed_at DESC LIMIT 1",
            (club_id,)
        ) as cur:
            diag = await cur.fetchone()

        # Récupérer les projets déjà en cours
        async with db.execute(
            "SELECT project_id FROM club_projects WHERE club_id = ?",
            (club_id,)
        ) as cur:
            existing = {row["project_id"] for row in await cur.fetchall()}

    profile = diag["profile"] if diag else "starter"
    profile_data = PROFILES[profile]
    recommended_difficulties = profile_data["recommended_difficulty"]

    # Taille → budget max indicatif
    size_budget = {"micro": 3000, "small": 8000, "medium": 20000, "large": 50000}
    budget_max = size_budget.get(club["size"], 5000)

    library = load_library()
    scored = []
    for p in library:
        if p["id"] in existing:
            continue  # déjà en cours
        score = 0
        # Critère 1 : difficulté compatible avec le profil
        if p["difficulty"] in recommended_difficulties:
            score += 40
        elif p["difficulty"] == min(recommended_difficulties) - 1:
            score += 20  # légèrement en dessous = accessible
        # Critère 2 : budget compatible
        if p["budget_min"] <= budget_max:
            score += 30
        # Critère 3 : thème sport féminin si club avec section féminine (heuristique)
        if p["theme"] in ["sante", "cohesion", "education"]:
            score += 10  # thèmes universels
        # Critère 4 : projets simples favorisés pour les débutants
        if profile == "starter" and p["difficulty"] == 1:
            score += 20

        scored.append({**p, "compatibility_score": score})

    scored.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return {
        "club_id":    club_id,
        "profile":    profile,
        "profile_label": profile_data["label"],
        "matches":    scored[:limit],
    }

"""
TerritoireSport — Routes Affinité club-territoire
Croisement entre profil club et problématiques territoire
"""

from fastapi import APIRouter, HTTPException
import json
import uuid
from pathlib import Path
from typing import List
from models.affinity import (
    AffinityScoreOut, AffinitySelection, AffinityResponse
)

router = APIRouter(prefix="/api/affinity", tags=["affinity"])

# ── Chargement des données ───────────────────────────────────
def load_json(filename: str):
    path = Path(f"data/{filename}")
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))

def load_themes():
    themes_list = load_json("themes.json")
    return {t["id"]: t for t in themes_list}

# ── Mapping sport → thématiques affinité ────────────────────
SPORT_THEME_AFFINITY = {
    "tennis de table": ["handicap", "intergenerationnel", "sante", "cohesion", "education"],
    "football": ["insertion", "cohesion", "education", "egalite", "sante"],
    "basketball": ["insertion", "cohesion", "education", "egalite"],
    "handball": ["insertion", "cohesion", "sante", "education"],
    "rugby": ["insertion", "cohesion", "education", "handicap"],
    "volley": ["sante", "intergenerationnel", "cohesion"],
    "natation": ["sante", "handicap", "intergenerationnel"],
    "athletisme": ["sante", "education", "environnement"],
    "cyclisme": ["environnement", "sante", "tourisme"],
    "judo": ["education", "insertion", "egalite", "handicap"],
    "tennis": ["sante", "intergenerationnel", "tourisme"],
    "badminton": ["sante", "intergenerationnel"],
    "gymnastique": ["sante", "education", "intergenerationnel"],
    "escalade": ["environnement", "sante", "handicap"],
    "aviron": ["environnement", "sante", "tourisme"],
    "kayak": ["environnement", "sante", "tourisme"],
    "voile": ["environnement", "tourisme", "handicap"],
    "equitation": ["handicap", "sante", "environnement", "intergenerationnel"],
    "golf": ["environnement", "sante", "tourisme"],
}

# ── Routes ───────────────────────────────────────────────────

@router.get("/{club_id}", response_model=AffinityResponse)
async def get_affinity(club_id: str):
    """Calcule l'affinité club-territoire pour toutes les thématiques"""
    import aiosqlite

    async with aiosqlite.connect("data/territoiresport.db") as db:
        # Récupérer le club
        cursor = await db.execute(
            "SELECT sport, size, members_count FROM clubs WHERE id = ?",
            (club_id,)
        )
        club = await cursor.fetchone()
        if not club:
            raise HTTPException(status_code=404, detail=f"Club {club_id} non trouvé")

        sport, size, members_count = club

        # Récupérer le dernier diagnostic
        cursor = await db.execute(
            "SELECT score, profile FROM diagnostics WHERE club_id = ? ORDER BY completed_at DESC LIMIT 1",
            (club_id,)
        )
        diagnostic = await cursor.fetchone()
        score = diagnostic[0] if diagnostic else 0
        profile = diagnostic[1] if diagnostic else "starter"

        # Récupérer le territoire
        from routes.territory import get_territory_by_club
        territory = await get_territory_by_club(club_id)

        # Récupérer les problématiques territoire
        from routes.territory import get_territory_diagnostic
        territory_diagnostics = await get_territory_diagnostic(territory["id"])

        # Calculer l'affinité pour chaque thématique
        themes = load_themes()
        affinity_scores = []

        for theme_id, theme in themes.items():
            score_sport = compute_sport_score(sport, theme_id)
            score_profil = compute_profil_score(profile, theme_id)
            score_taille = compute_taille_score(size, theme_id)
            score_ressources = compute_ressources_score(members_count, theme_id)
            score_total = score_sport + score_profil + score_taille + score_ressources

            affinity_scores.append({
                "id": f"{club_id}-{theme_id}",
                "club_id": club_id,
                "theme_id": theme_id,
                "theme_label": theme["label"],
                "theme_icon": theme["icon"],
                "score_sport": score_sport,
                "score_profil": score_profil,
                "score_taille": score_taille,
                "score_ressources": score_ressources,
                "score_total": score_total,
                "rank": None,
                "selected": False
            })

        # Trier par score décroissant
        affinity_scores.sort(key=lambda x: x["score_total"], reverse=True)
        for i, s in enumerate(affinity_scores):
            s["rank"] = i + 1

        # Top 3 recommandées
        recommended = [s["theme_id"] for s in affinity_scores[:3]]

        # Récupérer les sélections existantes
        cursor = await db.execute(
            "SELECT theme_id FROM affinity_scores WHERE club_id = ? AND selected = 1",
            (club_id,)
        )
        selected = [row[0] for row in await cursor.fetchall()]

        return {
            "scores": affinity_scores,
            "recommended": recommended,
            "selected": selected
        }

@router.post("/save", response_model=AffinityResponse)
async def save_affinity(selection: AffinitySelection):
    """Sauvegarde la sélection de thématiques d'action"""
    import aiosqlite

    if len(selection.theme_ids) > 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum 3 thématiques peuvent être sélectionnées"
        )

    async with aiosqlite.connect("data/territoiresport.db") as db:
        # Désélectionner toutes les anciennes
        await db.execute(
            "UPDATE affinity_scores SET selected = 0 WHERE club_id = ?",
            (selection.club_id,)
        )

        # Sélectionner les nouvelles
        for theme_id in selection.theme_ids:
            await db.execute(
                """INSERT OR REPLACE INTO affinity_scores
                   (id, club_id, theme_id, score_sport, score_profil, score_taille, score_ressources, score_total, rank, selected)
                   VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, 1)""",
                (str(uuid.uuid4()), selection.club_id, theme_id)
            )

        await db.commit()

    # Retourner l'affinité mise à jour
    return await get_affinity(selection.club_id)

# ── Algorithmes de scoring ───────────────────────────────────

def compute_sport_score(sport: str, theme_id: str) -> int:
    """Score sport (0-30) : affinité sport ↔ thématique"""
    sport_lower = sport.lower()
    affinities = SPORT_THEME_AFFINITY.get(sport_lower, [])

    if theme_id in affinities[:3]:  # Top 3 = affinité forte
        return 30
    elif theme_id in affinities:  # Autres = affinité moyenne
        return 20
    else:
        return 10  # Baseline

def compute_profil_score(profile: str, theme_id: str) -> int:
    """Score profil (0-30) : maturité club ↔ difficulté thématique"""
    # Les profils "pioneer" et "engaged" peuvent tackle des thématiques complexes
    # Les profils "emerging" et "starter" doivent commencer simple

    complex_themes = ["insertion", "handicap", "egalite", "environnement"]
    medium_themes = ["cohesion", "education", "sante", "economie"]
    simple_themes = ["culture", "tourisme", "intergenerationnel"]

    if profile in ["pioneer", "engaged"]:
        if theme_id in complex_themes:
            return 30
        elif theme_id in medium_themes:
            return 25
        else:
            return 20
    elif profile == "emerging":
        if theme_id in medium_themes:
            return 30
        elif theme_id in simple_themes:
            return 25
        else:
            return 15
    else:  # starter
        if theme_id in simple_themes:
            return 30
        elif theme_id in medium_themes:
            return 20
        else:
            return 10

def compute_taille_score(size: str, theme_id: str) -> int:
    """Score taille (0-20) : taille club ↔ ambition thématique"""
    # Clubs large/medium = projets ambitieux
    # Clubs small/micro = projets modestes

    ambitious_themes = ["insertion", "environnement", "handicap", "economie"]

    if size in ["large", "medium"]:
        if theme_id in ambitious_themes:
            return 20
        else:
            return 15
    else:  # small, micro
        if theme_id in ambitious_themes:
            return 10
        else:
            return 20

def compute_ressources_score(members_count: int, theme_id: str) -> int:
    """Score ressources (0-20) : nombre licenciés ↔ capacité mobilisation"""
    # Plus de licenciés = plus de capacité

    if members_count > 200:
        return 20
    elif members_count > 100:
        return 15
    elif members_count > 50:
        return 10
    else:
        return 5
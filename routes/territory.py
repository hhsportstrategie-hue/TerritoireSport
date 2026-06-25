"""
TerritoireSport — Routes Territoire
Carte d'identité + Diagnostic territorial + Acteurs non-marchands
"""

from fastapi import APIRouter, HTTPException
import json
from pathlib import Path
from models.territory import (
    TerritoryOut, TerritoryDiagnosticOut, TerritoryActorOut, TerritoryFullOut
)

router = APIRouter(prefix="/api/territory", tags=["territory"])

# ── Chargement des données statiques ─────────────────────────
def load_json(filename: str):
    path = Path(f"data/{filename}")
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))

def load_themes():
    """Retourne les 19 thématiques indexées par ID"""
    themes_list = load_json("themes.json")
    return {t["id"]: t for t in themes_list}

# ── Routes ───────────────────────────────────────────────────

@router.get("/{territory_id}", response_model=TerritoryOut)
async def get_territory(territory_id: str):
    """Carte d'identité d'un territoire"""
    territories = load_json("territories.json")
    territory = next((t for t in territories if t["id"] == territory_id), None)
    if not territory:
        raise HTTPException(status_code=404, detail=f"Territoire {territory_id} non trouvé")
    return territory

@router.get("/{territory_id}/diagnostic", response_model=list[TerritoryDiagnosticOut])
async def get_territory_diagnostic(territory_id: str):
    """Problématiques territoriales scorées (top 5)"""
    territories = load_json("territories.json")
    territory = next((t for t in territories if t["id"] == territory_id), None)
    if not territory:
        raise HTTPException(status_code=404, detail=f"Territoire {territory_id} non trouvé")

    themes = load_themes()
    actors = load_json("territory_actors.json")

    # Acteurs présents sur ce territoire
    territory_actors = [a for a in actors if a.get("territory_id") == territory_id]

    # Comptage des acteurs par thématique
    actors_by_theme = {}
    for actor in territory_actors:
        for theme_id in actor.get("themes", []):
            actors_by_theme[theme_id] = actors_by_theme.get(theme_id, 0) + 1

    # Calcul des scores
    diagnostics = []
    # Pour chaque thématique, calculer score factuel + score acteurs
    # Score factuel basé sur les caractéristiques du territoire
    for theme_id, theme in themes.items():
        # Score factuel (0-50) : basé sur les indicateurs territoire
        score_factuel = compute_factual_score(territory, theme_id)

        # Score acteurs (0-50) : basé sur la présence d'acteurs
        actor_count = actors_by_theme.get(theme_id, 0)
        score_acteurs = min(50, actor_count * 10)  # 1 acteur = 10 pts, max 50

        score_total = score_factuel + score_acteurs

        if score_total > 0:  # Ne garder que les thématiques pertinentes
            diagnostics.append({
                "id": f"{territory_id}-{theme_id}",
                "territory_id": territory_id,
                "theme_id": theme_id,
                "theme_label": theme["label"],
                "theme_icon": theme["icon"],
                "theme_color": theme["color"],
                "score_factuel": score_factuel,
                "score_acteurs": score_acteurs,
                "score_total": score_total,
                "rank": None
            })

    # Trier par score décroissant et assigner les rangs
    diagnostics.sort(key=lambda x: x["score_total"], reverse=True)
    for i, d in enumerate(diagnostics[:10]):  # Top 10
        d["rank"] = i + 1

    return diagnostics[:10]

@router.get("/{territory_id}/actors", response_model=list[TerritoryActorOut])
async def get_territory_actors(territory_id: str):
    """Acteurs non-marchands présents sur le territoire"""
    actors = load_json("territory_actors.json")
    territory_actors = [a for a in actors if a.get("territory_id") == territory_id]
    return territory_actors

@router.get("/{territory_id}/full", response_model=TerritoryFullOut)
async def get_territory_full(territory_id: str):
    """Vue complète : carte + diagnostic + acteurs"""
    territory = await get_territory(territory_id)
    diagnostics = await get_territory_diagnostic(territory_id)
    actors = await get_territory_actors(territory_id)

    # Top 5 thématiques
    top_themes = [d["theme_id"] for d in diagnostics[:5]]

    return {
        "territory": territory,
        "diagnostics": diagnostics,
        "actors": actors,
        "top_themes": top_themes
    }

@router.get("/by-club/{club_id}", response_model=TerritoryOut)
async def get_territory_by_club(club_id: str):
    """Récupère le territoire d'un club"""
    import aiosqlite
    async with aiosqlite.connect("data/territoiresport.db") as db:
        # Vérifier que le club existe
        cursor = await db.execute("SELECT city, department FROM clubs WHERE id = ?", (club_id,))
        club = await cursor.fetchone()
        if not club:
            raise HTTPException(status_code=404, detail=f"Club {club_id} non trouvé")

        # Chercher le territoire correspondant
        city, department = club
        territories = load_json("territories.json")
        territory = next(
            (t for t in territories
             if t.get("department") == department and t.get("city") == city),
            None
        )
        if not territory:
            # Fallback : territoire par département
            territory = next(
                (t for t in territories if t.get("department") == department),
                None
            )
        if not territory:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun territoire trouvé pour {city} ({department})"
            )
        return territory

# ── Algorithmes de scoring ───────────────────────────────────

def compute_factual_score(territory: dict, theme_id: str) -> int:
    """
    Score factuel (0-50) basé sur les indicateurs territoire.
    Chaque thématique a ses propres critères.
    """
    score = 0

    # Récupérer les indicateurs
    unemployment = territory.get("unemployment", 0) or 0
    median_income = territory.get("median_income", 0) or 0
    qpv_count = territory.get("qpv_count", 0) or 0
    population = territory.get("population", 0) or 0
    median_age = territory.get("median_age", 0) or 0

    # Critères par thématique (max 50 pts)
    if theme_id == "insertion":
        # Insertion : chômage élevé + QPV + revenus faibles
        if unemployment > 10: score += 20
        elif unemployment > 7: score += 10
        if qpv_count > 0: score += 15
        if median_income < 20000: score += 15

    elif theme_id == "cohesion":
        # Cohésion : QPV + densité + chômage
        if qpv_count > 0: score += 20
        if population > 10000: score += 10
        if unemployment > 8: score += 20

    elif theme_id == "sante":
        # Santé : âge médian + chômage + revenus
        if median_age > 40: score += 20
        if unemployment > 8: score += 15
        if median_income < 22000: score += 15

    elif theme_id == "education":
        # Éducation : population jeune
        if median_age < 35: score += 25
        if population > 5000: score += 15
        if qpv_count > 0: score += 10

    elif theme_id == "environnement":
        # Environnement : densité (zones rurales = + pertinent)
        if population < 5000: score += 25
        if median_income > 22000: score += 15
        score += 10  # Baseline

    elif theme_id == "culture":
        # Culture : densité urbaine
        if population > 10000: score += 25
        if median_age < 40: score += 15
        score += 10

    elif theme_id == "economie":
        # Économie : chômage + revenus
        if unemployment > 8: score += 20
        if median_income < 22000: score += 20
        score += 10

    elif theme_id == "handicap":
        # Handicap : densité + revenus
        if population > 5000: score += 20
        if median_income < 22000: score += 15
        score += 15

    elif theme_id == "intergenerationnel":
        # Intergénérationnel : âge médian élevé
        if median_age > 42: score += 25
        if population > 5000: score += 15
        score += 10

    elif theme_id == "egalite":
        # Égalité : chômage + revenus
        if unemployment > 8: score += 20
        if median_income < 22000: score += 20
        score += 10

    else:
        # Thématiques sans critères spécifiques : score baseline
        score += 15

    return min(50, score)
"""
TerritoireSport — Route Shortlist
Croise profil club + partenaires du territoire pour proposer une shortlist qualifiée.
"""
from fastapi import APIRouter, HTTPException
from db_config import DB_PATH
import json
import sqlite3

router = APIRouter(prefix="/api/shortlist", tags=["shortlist"])


@router.get("/{club_id}")
async def get_shortlist(club_id: str, themes: str = "cohesion,inclusion", limit: int = 10):
    """
    Génère une shortlist de partenaires pour un club.
    Filtre : département du club + thèmes sélectionnés.
    Score : nombre de thèmes en commun + bonus type (public/associatif/privé).
    """
    theme_list = [t.strip() for t in themes.split(",") if t.strip()]
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Récupérer le club
    cur.execute("SELECT id, name, sport, city, department FROM clubs WHERE id = ?", (club_id,))
    club_row = cur.fetchone()
    if not club_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Club introuvable")
    club = dict(club_row)

    # Récupérer tous les partenaires du département
    cur.execute(
        "SELECT id, name, type, category, city, department, contact_email, contact_url, description, themes FROM partners WHERE department = ?",
        (club["department"],)
    )
    partners = [dict(row) for row in cur.fetchall()]
    conn.close()

    # Calculer un score pour chaque partenaire
    scored = []
    for p in partners:
        try:
            p_themes = json.loads(p.get("themes", "[]"))
        except (json.JSONDecodeError, TypeError):
            p_themes = []

        # Score = nombre de thèmes en commun * 10 + bonus type
        common = set(p_themes) & set(theme_list)
        score = len(common) * 10

        # Bonus type : public/associatif = +5 (plus accessible pour club amateur)
        if p.get("type") in ("public", "association"):
            score += 5

        # Bonus si même ville
        if p.get("city") and club.get("city") and p["city"].lower() == club["city"].lower():
            score += 3

        scored.append({
            "id": p["id"],
            "name": p["name"],
            "type": p["type"],
            "category": p["category"],
            "city": p["city"],
            "description": p["description"],
            "contact_email": p["contact_email"],
            "contact_url": p["contact_url"],
            "themes": p_themes,
            "matching_themes": list(common),
            "score": score,
        })

    # Trier par score décroissant
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Limiter
    shortlist = scored[:limit]

    return {
        "club": {
            "id": club["id"],
            "name": club["name"],
            "sport": club["sport"],
            "city": club["city"],
            "department": club["department"],
        },
        "themes_requested": theme_list,
        "total_partners_in_territory": len(partners),
        "shortlist": shortlist,
        "count": len(shortlist),
    }
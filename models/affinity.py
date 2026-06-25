"""
TerritoireSport — Modèles Affinité club-territoire
Croisement entre profil club et problématiques territoire
"""

from pydantic import BaseModel
from typing import Optional, List

class AffinityScoreOut(BaseModel):
    """Score d'affinité club-territoire pour une thématique"""
    id:              str
    club_id:         str
    theme_id:        str
    theme_label:     str
    theme_icon:      str
    score_sport:     int  # 0-30
    score_profil:    int  # 0-30
    score_taille:    int  # 0-20
    score_ressources: int  # 0-20
    score_total:     int  # 0-100
    rank:            Optional[int]
    selected:        bool

class AffinitySelection(BaseModel):
    """Sélection des thématiques d'action par le club"""
    club_id:     str
    theme_ids:   List[str]  # 3 thématiques max

class AffinityResponse(BaseModel):
    """Réponse complète affinité"""
    scores:          List[AffinityScoreOut]
    recommended:     List[str]  # Top 3 IDs
    selected:        List[str]  # Thématiques retenues par le club
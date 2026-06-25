"""
TerritoireSport — Modèles Territoire
Carte d'identité territoire + Diagnostic territorial + Acteurs non-marchands
"""

from pydantic import BaseModel
from typing import Optional, List

class TerritoryOut(BaseModel):
    """Carte d'identité d'un territoire"""
    id:              str
    epci:            str
    bassin_vie:      Optional[str]
    department:      str
    region:          str
    population:      Optional[int]
    density:         Optional[int]
    median_age:      Optional[float]
    median_income:   Optional[int]
    unemployment:    Optional[float]
    qpv_count:       Optional[int]

class TerritoryDiagnosticOut(BaseModel):
    """Problématique territoriale scorée"""
    id:              str
    territory_id:    str
    theme_id:        str
    theme_label:     str
    theme_icon:      str
    theme_color:     str
    score_factuel:   int  # 0-50
    score_acteurs:   int  # 0-50
    score_total:     int  # 0-100
    rank:            Optional[int]

class TerritoryActorOut(BaseModel):
    """Acteur non-marchand présent sur le territoire"""
    id:              str
    territory_id:    str
    name:            str
    type:            str  # 'association' | 'public' | 'fondation'
    themes:          List[str]
    city:            Optional[str]
    contact_email:   Optional[str] = None
    contact_phone:   Optional[str] = None
    contact_phone:   Optional[str]

class TerritoryFullOut(BaseModel):
    """Vue complète : carte + diagnostic + acteurs"""
    territory:       TerritoryOut
    diagnostics:     List[TerritoryDiagnosticOut]
    actors:          List[TerritoryActorOut]
    top_themes:      List[str]  # IDs des 5 thématiques les plus pertinentes
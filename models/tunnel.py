"""
Modèles Pydantic pour le Tunnel d'Ingénierie de Projet.
"""

from pydantic import BaseModel
from typing import Optional, Dict, List


# ── Diagnostic ressources (5 questions) ──────────────────────────

class DiagnosticRessourcesSubmit(BaseModel):
    club_id: str
    reponses: Dict[str, int]  # {"benevoles": 2, "salaries": 1, "budget": 2, "deadline": 3, "experience": 2}


class DiagnosticRessourcesOut(BaseModel):
    id: str
    club_id: str
    score_total: int
    niveau: str  # "micro", "simple", "intermediaire", "structurant"
    description: str
    projets_recommandes: List[str]
    reponses: Dict[str, int]
    completed_at: str


# ── Tunnel 7 étapes ───────────────────────────────────────────────

    club_id: Optional[str] = None  # Informational only - non requis par la route (club_id vient du projet)
    club_id: str
    projet_id: Optional[str] = None  # ID du projet en construction
    etape_numero: int  # 1-7
    contenu: Dict  # Contenu spécifique à l'étape
    complete: bool = False


class TunnelProjetCreate(BaseModel):
    club_id: str
    titre: str
    description: Optional[str] = None
    thematique: Optional[str] = None


class TunnelProjetOut(BaseModel):
    id: str
    club_id: str
    titre: str
    description: Optional[str]
    thematique: Optional[str]
    etape_actuelle: int
    progression: int  # % 0-100
    created_at: str
    updated_at: str


class TunnelEtapeOut(BaseModel):
    id: str
    projet_id: str
    etape_numero: int
    contenu: Dict
    complete: bool
    created_at: str
    updated_at: str


# ── Scoring de faisabilité ─────────────────────────────────────────

class ScoringFaisabiliteSubmit(BaseModel):
    club_id: str
    projet_id: Optional[str] = None
    scores: Dict[str, int]  # {"alignement_territoire": 12, "capacite_humaine": 10, ...}


class ScoringFaisabiliteOut(BaseModel):
    id: str
    club_id: str
    projet_id: Optional[str]
    score_total: int
    niveau: str  # "non_faisable", "difficile", "faisable", "tres_faisable", "excellent"
    couleur: str
    recommandation: str
    scores: Dict[str, int]
    completed_at: str
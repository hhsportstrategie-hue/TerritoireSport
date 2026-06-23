from pydantic import BaseModel
from typing import Optional

# Les 10 questions du diagnostic territorial
DIAGNOSTIC_QUESTIONS = [
    {"id": "q1", "text": "Votre club a-t-il déjà mené un projet à impact social ou territorial ?",
     "options": ["Jamais", "Une fois", "Régulièrement"]},
    {"id": "q2", "text": "Avez-vous des partenaires institutionnels (mairie, département, région) ?",
     "options": ["Aucun", "1-2 partenaires", "3 partenaires ou plus"]},
    {"id": "q3", "text": "Quelle est votre capacité à mobiliser des bénévoles pour un nouveau projet ?",
     "options": ["Difficile", "Possible avec effort", "Facile — nous avons des ressources"]},
    {"id": "q4", "text": "Avez-vous déjà déposé un dossier de subvention (ANS, DRAJES, Région…) ?",
     "options": ["Jamais", "Une fois", "Régulièrement"]},
    {"id": "q5", "text": "Votre club dispose-t-il d'un budget dédié au développement (hors fonctionnement) ?",
     "options": ["Non", "Moins de 2 000 €", "Plus de 2 000 €"]},
    {"id": "q6", "text": "Avez-vous des liens avec des associations ou structures du territoire (hors sport) ?",
     "options": ["Aucun", "Quelques liens informels", "Partenariats formalisés"]},
    {"id": "q7", "text": "Votre club est-il présent sur les réseaux sociaux et communique-t-il régulièrement ?",
     "options": ["Non ou rarement", "Oui mais sans stratégie", "Oui avec une stratégie"]},
    {"id": "q8", "text": "Avez-vous des membres du CA formés à la gestion de projet ou à la recherche de financements ?",
     "options": ["Non", "1 personne", "2 personnes ou plus"]},
    {"id": "q9", "text": "Quel est votre niveau de connaissance des dispositifs de financement du sport ?",
     "options": ["Très faible", "Moyen", "Bon"]},
    {"id": "q10","text": "Êtes-vous prêt à consacrer du temps (2-4h/semaine) à un projet territorial sur 6-12 mois ?",
     "options": ["Non", "Peut-être", "Oui, nous sommes motivés"]},
]

PROFILES = {
    "pioneer": {
        "label": "Pionnier",
        "min_score": 20,
        "description": "Votre club est prêt à lancer des projets ambitieux. Vous avez les ressources, le réseau et l'expérience.",
        "recommended_difficulty": [3, 4],
        "color": "#2D6A4F",
    },
    "engaged": {
        "label": "Engagé",
        "min_score": 13,
        "description": "Votre club a de bonnes bases. Quelques projets structurants vous permettront de monter en puissance.",
        "recommended_difficulty": [2, 3],
        "color": "#52B788",
    },
    "emerging": {
        "label": "Émergent",
        "min_score": 7,
        "description": "Votre club commence à s'ouvrir au territoire. Des projets simples et bien accompagnés vous aideront à progresser.",
        "recommended_difficulty": [1, 2],
        "color": "#F4A261",
    },
    "starter": {
        "label": "Débutant",
        "min_score": 0,
        "description": "C'est votre premier pas vers l'impact territorial. Commencez par un projet simple, avec de l'aide.",
        "recommended_difficulty": [1],
        "color": "#E74C3C",
    },
}

def compute_profile(score: int) -> str:
    for profile, data in PROFILES.items():
        if score >= data["min_score"]:
            return profile
    return "starter"

class DiagnosticSubmit(BaseModel):
    club_id: str
    answers: dict  # {"q1": 0, "q2": 2, ...} — index de l'option choisie

class DiagnosticOut(BaseModel):
    id:          str
    club_id:     str
    score:       int
    profile:     str
    profile_label: str
    profile_desc:  str
    completed_at:  str

# TerritoireSport 🏅

**Plateforme d'aide aux clubs et associations sportives pour monter et piloter des projets à impact local.**

MVP cible : journée de formation ES Coutances — octobre 2026.

## Concept

TerritoireSport accompagne les clubs sportifs dans leur développement territorial :
diagnostic, identification de projets pertinents, mise en relation avec des partenaires,
suivi des projets et mesure de l'impact.

## Fonctionnalités MVP (F0 à F8)

| ID | Fonctionnalité |
|----|---------------|
| F0 | Landing page + inscription club |
| F1 | Profil club (infos, sport, territoire, taille) |
| F2 | Diagnostic territorial (10 questions → score d'impact potentiel) |
| F3 | Bibliothèque de projets (19 thématiques) |
| F4 | Matching automatique club ↔ projets |
| F5 | Fiche projet détaillée (description, partenaires, budget, indicateurs) |
| F6 | Tableau de bord club (projets en cours, statuts) |
| F7 | Annuaire partenaires (par territoire) |
| F8 | Export rapport d'impact (PDF) |

## Stack technique

- **Backend** : Python FastAPI
- **Base de données** : SQLite
- **Frontend** : HTML/CSS/JS vanilla (compatible PWA)
- **Déployable** partout sans infrastructure complexe

## Installation

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Ouvrir http://localhost:8000
```

## Structure

```
TerritoireSport/
├── main.py              # FastAPI app + configuration
├── models/              # Modèles Pydantic + SQLite
├── routes/              # Endpoints API
├── data/                # Données statiques (thématiques, projets)
├── frontend/            # Interface HTML/CSS/JS
└── docs/                # Documentation
```

## Les 19 thématiques sociétales

Santé & bien-être, Insertion professionnelle, Cohésion sociale, Environnement,
Éducation & jeunesse, Égalité femmes-hommes, Handicap & inclusion, Seniors,
Prévention des violences, Culture & patrimoine, Économie locale, Tourisme,
Mobilité, Numérique & innovation, Gouvernance participative, Sport de haut niveau,
Sport féminin, Sport amateur, Sport scolaire.

## Auteur

Développé par H3P Solutions — Hervé HUET.
Premier utilisateur cible : US Ducey (club football, Manche).

---
*TerritoireSport — H3P Solutions 2026*

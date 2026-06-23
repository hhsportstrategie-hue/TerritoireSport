# TerritoireSport — Architecture technique

## Vue d'ensemble

```
Navigateur (HTML vanilla)       FastAPI (Python)          SQLite
┌──────────────────────┐        ┌──────────────────┐      ┌──────────────────┐
│  frontend/           │  HTTP  │  main.py         │      │  territoiresport │
│  ├─ index.html   F0  │◄──────►│  routes/         │◄────►│  .db             │
│  ├─ diagnostic   F2  │        │  ├─ clubs.py     │      │                  │
│  ├─ projects     F3-5│        │  ├─ diagnostic.py│      │  clubs           │
│  └─ dashboard    F6-8│        │  ├─ projects.py  │      │  diagnostics     │
└──────────────────────┘        │  └─ matching.py  │      │  club_projects   │
                                │  models/          │      │  partners        │
                                │  data/            │      └──────────────────┘
                                │  ├─ themes.json   │
                                │  └─ projects_     │
                                │    library.json   │
                                └──────────────────┘
```

## Fonctionnalités MVP

| ID | Page | Endpoint(s) |
|----|------|-------------|
| F0 | index.html | POST /api/clubs/register, POST /api/clubs/login |
| F1 | index.html (modal) | GET/PATCH /api/clubs/:id |
| F2 | diagnostic.html | GET /api/diagnostic/questions, POST /api/diagnostic/submit |
| F3 | projects.html | GET /api/projects/library |
| F4 | projects.html | GET /api/matching/:club_id |
| F5 | projects.html (modal) | GET /api/projects/library/:id |
| F6 | dashboard.html | GET /api/projects/club/:club_id, PATCH /api/projects/club/:id |
| F7 | dashboard.html | GET /api/partners/ |
| F8 | dashboard.html | GET /api/clubs/:id/rapport-pdf |

## Algorithme de matching (F4)

Score de compatibilité (0-100) basé sur 3 critères :
1. **Profil diagnostic** (40 pts) : difficulté du projet compatible avec le profil du club
2. **Budget** (30 pts) : budget minimum du projet ≤ budget indicatif de la taille du club
3. **Thème** (10-20 pts) : bonus pour les thèmes universels ou profil débutant

Profils :
- **Pionnier** (score 20/20) → projets de difficulté 3-4
- **Engagé** (13-19) → projets de difficulté 2-3
- **Émergent** (7-12) → projets de difficulté 1-2
- **Débutant** (0-6) → projets de difficulté 1

## Déploiement

```bash
# Installation
pip install -r requirements.txt

# Développement
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

# Documentation API auto-générée
http://localhost:8000/docs
```

## Sécurité (MVP)

- Mots de passe hashés SHA-256 (à remplacer par bcrypt en production)
- Authentification par UUID (à remplacer par JWT en production)
- Pas d'exposition des données sensibles entre clubs

## Données de démonstration

Au démarrage, 5 partenaires de démonstration sont automatiquement ajoutés :
- Mairie de Ducey-Les Chéris (50)
- DRAJES Normandie (14)
- Ligue de Football de Normandie (14)
- CINS Caen (14)
- ANS — Agence Nationale du Sport

## Extension prévue (post-MVP)

- F9 : Messagerie entre clubs
- F10 : Partage de bonnes pratiques
- F11 : Intégration TerritoireSport Ligue (B2B2C)
- F12 : Tableau de bord DRAJES/Région (agrégation)

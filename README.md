# TerritoireSport v3

Plateforme d'aide aux clubs sportifs pour monter des projets à impact local.

## 🚀 Démarrage rapide (local)

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Initialiser la DB + données démo
python3 seed.py

# 3. Lancer le serveur
uvicorn main:app --host 0.0.0.0 --port 8000
```

L'app est accessible sur http://localhost:8000

## 📡 Endpoints API

### Clubs
- `POST /api/clubs/register` — Inscription
- `POST /api/clubs/login` — Connexion
- `GET /api/clubs/{club_id}` — Profil club
- `PATCH /api/clubs/{club_id}` — Mise à jour profil

### Diagnostic
- `GET /api/diagnostic/questions` — Questions du diagnostic
- `POST /api/diagnostic/submit` — Soumettre réponses
- `GET /api/diagnostic/latest/{club_id}` — Dernier diagnostic

### Affinité
- `GET /api/affinity/{club_id}` — Top 5 thématiques d'affinité

### Projets
- `GET /api/projects/library` — Bibliothèque de 33 projets
- `GET /api/projects/library/{project_id}` — Détail projet
- `GET /api/projects/themes` — 19 thématiques
- `GET /api/projects/cas-inspirants` — 17 cas inspirants
- `POST /api/projects/club` — Créer projet club
- `GET /api/projects/club/{club_id}` — Projets du club

### Matching
- `GET /api/matching/{club_id}` — Partenaires matchés (top 5)

### Territoire
- `GET /api/territory/{territory_id}` — Carte d'identité
- `GET /api/territory/{territory_id}/diagnostic` — Problématiques scorées
- `GET /api/territory/{territory_id}/actors` — Acteurs non-marchands
- `GET /api/territory/{territory_id}/full` — Vue complète
- `GET /api/territory/by-club/{club_id}` — Territoire d'un club

### Partenaires
- `GET /api/partners/` — Liste (filtres: department, theme)

### Export
- `GET /api/clubs/{club_id}/rapport-pdf` — Rapport d'impact PDF

### Santé
- `GET /api/health` — Status

## 🚂 Déploiement Railway

### Configuration
- `Procfile` : `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- `nixpacks.toml` : Python 3.11 + pip
- `runtime.txt` : python-3.11.9

### Variables d'environnement
- `DB_PATH` (optionnel) : chemin vers la DB SQLite. Défaut : `data/territoiresport.db`

### ⚠️ SQLite éphémère
Par défaut, Railway ne persiste pas les données SQLite entre les redeploys.
Pour persister, ajouter un **volume** :
1. Railway Dashboard → Service → Settings → Volumes
2. Mount path : `/data`
3. Variable d'env : `DB_PATH=/data/territoiresport.db`

### Alternative : PostgreSQL
Pour une vraie prod, migrer vers PostgreSQL (Railway fournit un addon gratuit).

## 🧪 Tests

```bash
# Lancer le seed
python3 seed.py

# Tester les endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/affinity/90f8a193-a4b8-4975-b315-8e1484cdf3a3
curl http://localhost:8000/api/territory/argentan-intercom/full
```

## 📁 Structure

```
territoiresport/
├── main.py              # Point d'entrée FastAPI
├── seed.py              # Script de seed (idempotent)
├── db_config.py         # Configuration DB_PATH
├── routes/              # Routes API par domaine
│   ├── clubs.py
│   ├── diagnostic.py
│   ├── projects.py
│   ├── matching.py
│   ├── territory.py
│   └── affinity.py
├── models/              # Modèles Pydantic
├── data/                # Données statiques + DB
│   ├── schema.sql
│   ├── territories.json
│   ├── territory_actors.json
│   ├── themes.json
│   ├── projects_library.json
│   ├── cas_inspirants.json
│   └── territoiresport.db
├── frontend/            # HTML/CSS/JS
│   ├── index.html
│   ├── dashboard.html
│   ├── diagnostic.html
│   ├── projects.html
│   └── territoire.html
├── requirements.txt
├── Procfile
├── nixpacks.toml
└── runtime.txt
```

## 🎯 Club de démo

- ID : `90f8a193-a4b8-4975-b315-8e1484cdf3a3`
- Nom : BATT Argentan
- Sport : Tennis de table
- Ville : Argentan (61)
- Diagnostic : score 15/20, profil "Engagé"
- Top 3 affinités : Santé (85), Handicap (80), Cohésion (75)

## 📊 Données chargées

| Table/Source | Contenu |
|---|---|
| clubs | 1 club démo (BATT) |
| diagnostics | 1 diagnostic (engaged) |
| club_territories | Lien BATT ↔ Argentan Intercom |
| partners | 7 partenaires (Mairie, DRAJES, ANS, etc.) |
| funding_sources | 4 sources (ANS, Région, CD61, FdF) |
| territories.json | 8 EPCI normands |
| territory_actors.json | ~50 acteurs non-marchands |
| themes.json | 19 thématiques |
| projects_library.json | 33 projets types |
| cas_inspirants.json | 17 cas inspirants |
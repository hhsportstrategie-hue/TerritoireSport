# TerritoireSport — Architecture globale v2 (parcours utilisateur en 6 étapes)

## Vue d'ensemble du parcours utilisateur

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : Inscription + Diagnostic + Identification territoire       │
│  ÉTAPE 2 : Carte d'identité stratégique du territoire                  │
│  ÉTAPE 3 : Découverte base de données + propositions inspirantes        │
│  ÉTAPE 4 : Ingénierie de projet (Template)                             │
│  ÉTAPE 5 : Recherche financements + acteurs économiques                │
│  ÉTAPE 6 : Fiche projet complète                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

## Architecture cible

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (HTML/JS)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  F0-Accueil     │  F1-Diagnostic  │  F2-Territoire  │  F3-BDD          │
│  F4-Ingénierie  │  F5-Financements│  F6-Fiche projet │  Dashboard       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ HTTP
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        BACKEND FastAPI (Python)                         │
├─────────────────────────────────────────────────────────────────────────┤
│  routes/                                                                │
│  ├─ clubs.py          (F0-F1 : inscription, profil club)               │
│  ├─ diagnostic.py     (F1 : diagnostic territorial)                    │
│  ├─ territory.py      (F2 : carte d'identité territoire) ← NOUVEAU      │
│  ├─ projects.py       (F3 : bibliothèque + cas inspirants)             │
│  ├─ engineering.py    (F4 : template ingénierie projet) ← NOUVEAU      │
│  ├─ funding.py        (F5 : appels à projets + acteurs éco) ← NOUVEAU  │
│  ├─ fiche.py          (F6 : fiche projet complète) ← NOUVEAU           │
│  └─ matching.py       (matching intelligent)                           │
│                                                                         │
│  models/                                                                │
│  ├─ club.py, diagnostic.py, project.py, partner.py                     │
│  ├─ territory.py     ← NOUVEAU                                         │
│  ├─ engineering.py   ← NOUVEAU                                         │
│  ├─ funding.py       ← NOUVEAU                                         │
│  └─ fiche.py         ← NOUVEAU                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ SQL
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          BASE DE DONNÉES SQLite                         │
├─────────────────────────────────────────────────────────────────────────┤
│  clubs, diagnostics, club_projects, partners                           │
│  territories      ← NOUVEAU (carte d'identité territoire)              │
│  territory_actors ← NOUVEAU (acteurs non-marchands par territoire)     │
│  funding_sources  ← NOUVEAU (appels à projets)                         │
│  fiches_projet    ← NOUVEAU (fiches projet complètes)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DONNÉES STATIQUES (JSON)                       │
├─────────────────────────────────────────────────────────────────────────┤
│  data/themes.json              (19 thématiques)                         │
│  data/projects_library.json    (33 projets)                             │
│  data/cas_inspirants.json      (17 cas)                                 │
│  data/territories.json         ← NOUVEAU (données territoires)         │
│  data/funding_sources.json     ← NOUVEAU (base AAP)                     │
│  data/actors_non_marchands.json← NOUVEAU (base acteurs)                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Détail des 6 étapes

### ÉTAPE 1 — Inscription + Diagnostic + Identification territoire

**Objectif** : Le club s'inscrit, fait son diagnostic, identifie son territoire.

**Frontend** : `index.html` (inscription) + `diagnostic.html` (questionnaire)

**Backend** :
- `POST /api/clubs/register` — inscription
- `POST /api/clubs/login` — connexion
- `GET /api/diagnostic/questions` — questions du diagnostic
- `POST /api/diagnostic/submit` — soumission du diagnostic
- `GET /api/diagnostic/latest/{club_id}` — dernier diagnosticomme

**Données collectées** :
- Profil du club (sport, taille, ville, département)
- Réponses au diagnostic (10 questions, score 0-20)
- Profil résultant (Pionnier / Engagé / Émergent / Débutant)
- Territoire identifié (EPCI, bassin de vie, caractéristiques)

### ÉTAPE 2 — Carte d'identité stratégique du territoire

**Objectif** : Identifier les thématiques sociétales les plus pertinentes pour le territoire et les acteurs non-marchands présents.

**Frontend** : Nouvelle page `territoire.html`

**Backend** :
- `GET /api/territory/{club_id}` — carte d'identité du territoire
- `GET /api/territory/{club_id}/themes` — thématiques pertinentes (scorées)
- `GET /api/territory/{club_id}/actors` — acteurs non-marchands du territoire

**Algorithme de scoring des thématiques** :
1. **Critères de problématiques** (40 pts) : données INSEE, diagnostics territoriaux
2. **Présence d'acteurs** (40 pts) : nombre d'acteurs non-marchands actifs sur la thématique
3. **Profil du club** (20 pts) : affinité avec le sport et la taille du club

**Données affichées** :
- Carte d'identité : population, densité, âge, revenus, taux de chômage
- Top 5 thématiques pertinentes (avec score et justification)
- Liste des acteurs non-marchands par thématique

### ÉTAPE 3 — Découverte base de données + propositions inspirantes

**Objectif** : Présenter les projets existants et proposer les plus adaptés.

**Frontend** : `projects.html` (refonte avec filtres et recommandations)

**Backend** :
- `GET /api/projects/library` — bibliothèque de projets (avec filtres)
- `GET /api/projects/cas-inspirants` — cas inspirants (avec filtres)
- `GET /api/matching/{club_id}` — matching intelligent (refonte)

**Algorithme de matching amélioré** :
1. **Compatibilité territoire** (30 pts) : thématique du projet = thématique territoire
2. **Profil diagnostic** (25 pts) : difficulté compatible
3. **Budget** (20 pts) : budget projet ≤ budget club
4. **Acteurs disponibles** (15 pts) : acteurs non-marchands présents pour accompagner
5. **Cas inspirants similaires** (10 pts) : projets similaires déjà réalisés

### ÉTAPE 4 — Ingénierie de projet (Template)

**Objectif** : Construire le projet retenu via un template structuré.

**Frontend** : Nouvelle page `engineering.html` (formulaire multi-étapes)

**Backend** :
- `POST /api/engineering/start` — démarrer un projet
- `POST /api/engineering/{project_id}/step` — valider une étape
- `GET /api/engineering/{project_id}` — état du projet en cours

**Template d'ingénierie (8 étapes)** :
1. **Intention** — Pourquoi ce projet ? (besoin, contexte)
2. **Objectifs** — SMART (spécifique, mesurable, atteignable, réaliste, temporel)
3. **Public cible** — Bénéficiaires directs et indirects
4. **Activités** — Actions concrètes à mener
5. **Ressources humaines** — Bénévoles, salariés, partenaires
6. **Ressources financières** — Budget prévisionnel
7. **Calendrier** — Retro-planning
8. **Indicateurs** — KPIs de suivi et d'évaluation

### ÉTAPE 5 — Recherche financements + acteurs économiques

**Objectif** : Identifier les AAP et acteurs économiques pertinents.

**Frontend** : Nouvelle page `funding.html`

**Backend** :
- `GET /api/funding/aap` — appels à projets (nationaux, régionaux, locaux, thématisés)
- `GET /api/funding/actors` — acteurs économiques du territoire
- `GET /api/funding/match/{project_id}` — financements et acteurs adaptés

**Sources de données** :
- AAP nationaux : ANS, FDVA, Ministère des Sports
- AAP régionaux : Région Normandie, DRAJES
- AAP locaux : Départements, EPCI, Communes
- AAP thématisés : CPAM, CAF, Fondations (Fondation de France, Fondation de Normandie)
- Acteurs économiques : CCI, CMA, entreprises locales (via base SIRENE)

### ÉTAPE 6 — Fiche projet complète

**Objectif** : Synthétiser tous les éléments du projet.

**Frontend** : Nouvelle page `fiche.html` (lecture + export PDF)

**Backend** :
- `GET /api/fiche/{project_id}` — fiche complète
- `GET /api/fiche/{project_id}/pdf` — export PDF
- `POST /api/fiche/{project_id}/save` — sauvegarde

**Contenu de la fiche** :
- Thématique principale et secondaires
- Acteurs non-marchands identifiés
- Projets existants inspirants
- Ressources humaines mobilisées
- Budget prévisionnel
- Retro-planning
- Partenaires potentiels
- Appels à projets ciblés
- Indicateurs de suivi

## Modèle de données — Nouvelles tables

```sql
-- Territoires (carte d'identité)
CREATE TABLE territories (
    id              TEXT PRIMARY KEY,
    club_id         TEXT REFERENCES clubs(id),
    epci            TEXT,
    bassin_vie      TEXT,
    population      INTEGER,
    density         INTEGER,
    median_age      FLOAT,
    median_income   INTEGER,
    unemployment    FLOAT,
    qpv             INTEGER,  -- nombre de QPV
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Acteurs non-marchands par territoire
CREATE TABLE territory_actors (
    id              TEXT PRIMARY KEY,
    territory_id    TEXT REFERENCES territories(id),
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,  -- 'association' | 'public' | 'fondation'
    category        TEXT NOT NULL,  -- thématique
    city            TEXT,
    department      TEXT,
    themes          TEXT NOT NULL,  -- JSON array
    description     TEXT,
    contact         TEXT
);

-- Sources de financement
CREATE TABLE funding_sources (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,  -- 'national' | 'regional' | 'local' | 'thematic'
    organization    TEXT NOT NULL,
    themes          TEXT NOT NULL,  -- JSON array
    amount_min      INTEGER,
    amount_max      INTEGER,
    deadline        TEXT,
    url             TEXT,
    description     TEXT
);

-- Projets en cours d'ingénierie
CREATE TABLE engineering_projects (
    id              TEXT PRIMARY KEY,
    club_id         TEXT REFERENCES clubs(id),
    inspiration_id  TEXT,  -- projet inspirant
    intention       TEXT,
    objectives      TEXT,  -- JSON
    target_audience TEXT,
    activities      TEXT,  -- JSON
    human_resources TEXT,  -- JSON
    financial_resources TEXT,  -- JSON
    calendar        TEXT,  -- JSON
    indicators      TEXT,  -- JSON
    status          TEXT DEFAULT 'draft',
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Fiches projet complètes
CREATE TABLE fiches_projet (
    id              TEXT PRIMARY KEY,
    engineering_id  TEXT REFERENCES engineering_projects(id),
    club_id         TEXT REFERENCES clubs(id),
    theme_principal TEXT,
    themes_secondaires TEXT,  -- JSON
    acteurs_non_marchands TEXT,  -- JSON
    projets_inspirants TEXT,  -- JSON
    partenaires_potentiels TEXT,  -- JSON
    appels_projets TEXT,  -- JSON
    budget_total    INTEGER,
    created_at      TEXT DEFAULT (datetime('now'))
);
```

## Roadmap d'implémentation

| Phase | Contenu | Priorité |
|-------|---------|----------|
| **Phase 1** | ÉTAPE 1 (déjà fait) + ÉTAPE 2 (carte territoire) | 🔴 Haute |
| **Phase 2** | ÉTAPE 3 (refonte matching) + ÉTAPE 4 (template ingénierie) | 🟠 Moyenne |
| **Phase 3** | ÉTAPE 5 (base AAP + acteurs éco) + ÉTAPE 6 (fiche projet) | 🟡 Normale |

## Club pilote

**BATT — Bayard Tennis de Table Argentan** (61, Orne)
- Département : Orne
- Région : Normandie
- EPCI : Argentan Intercom
- Bassin de vie : Argentan
- Sport : Tennis de table
- Taille : Small (estimation)

## Prochaines actions

1. ✅ Valider l'architecture avec Hervé
2. ⏳ Implémenter ÉTAPE 2 (carte territoire)
3. ⏳ Enrichir la base de données territoires
4. ⏳ Refondre le matching (ÉTAPE 3)
5. ⏳ Créer le template d'ingénierie (ÉTAPE 4)
6. ⏳ Construire la base AAP (ÉTAPE 5)
7. ⏳ Créer la fiche projet (ÉTAPE 6)
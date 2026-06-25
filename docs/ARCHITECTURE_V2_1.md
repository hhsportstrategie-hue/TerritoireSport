# TerritoireSport — Architecture globale v2.1 (parcours utilisateur corrigé)

## Vue d'ensemble du parcours utilisateur

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : Inscription + Diagnostic club + Identification territoire  │
│  ÉTAPE 2 : Carte d'identité territoire + Diagnostic territorial       │
│  ÉTAPE 2bis : Affinité club-territoire                                 │
│  ÉTAPE 3 : Découverte BDD + Matching intelligent                       │
│  ÉTAPE 4 : Ingénierie projet (Template 6 étapes)                       │
│  ÉTAPE 5a : Recherche financements (AAP)                               │
│  ÉTAPE 5b : Identification partenaires économiques                    │
│  ÉTAPE 6 : Fiche projet complète (agrégation automatique)              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Architecture cible

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (HTML/JS)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  F0-Accueil     │  F1-Diagnostic  │  F2-Territoire  │  F3-BDD          │
│  F4-Ingénierie  │  F5a-Financements│  F5b-Partenaires│  F6-Fiche projet │
│  Dashboard "Mes projets en cours"                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ HTTP
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        BACKEND FastAPI (Python)                         │
├─────────────────────────────────────────────────────────────────────────┤
│  routes/                                                                │
│  ├─ clubs.py          (F1a : inscription, profil club)                 │
│  ├─ diagnostic.py     (F1b : diagnostic club)                          │
│  ├─ territory.py      (F2 : carte + diagnostic territoire)            │
│  ├─ affinity.py       (F2bis : affinité club-territoire)              │
│  ├─ projects.py       (F3 : bibliothèque + cas inspirants)             │
│  ├─ matching.py       (F3 : matching intelligent)                     │
│  ├─ engineering.py    (F4 : template ingénierie 6 étapes)             │
│  ├─ funding.py        (F5a : appels à projets)                         │
│  ├─ partners.py       (F5b : partenaires économiques)                  │
│  └─ fiche.py          (F6 : agrégation automatique)                    │
│                                                                         │
│  models/                                                                │
│  ├─ club.py, diagnostic.py, project.py, partner.py                     │
│  ├─ territory.py     (carte + acteurs territoire)                      │
│  ├─ affinity.py      (croisement club-territoire)                      │
│  ├─ engineering.py   (template 6 étapes + suivi avancement)           │
│  └─ funding.py       (AAP + critères éligibilité)                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ SQL
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          BASE DE DONNÉES SQLite                         │
├─────────────────────────────────────────────────────────────────────────┤
│  clubs, diagnostics, club_projects, partners                           │
│  club_territories      ← N-N club-territoire                           │
│  territories           ← carte d'identité territoire                   │
│  territory_diagnostics ← problématiques territoire                     │
│  territory_actors      ← acteurs non-marchands par territoire          │
│  affinity_scores       ← croisement club-territoire                    │
│  engineering_projects  ← projets en cours d'ingénierie                 │
│  project_steps         ← suivi avancement template (6 étapes)          │
│  project_inspirations  ← N-N projet-cas inspirants                     │
│  funding_sources       ← base AAP                                      │
│  funding_eligibility   ← critères éligibilité par AAP                  │
│  club_funding_matches  ← AAP adaptés au projet                         │
│  club_partner_matches  ← partenaires économiques adaptés               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DONNÉES STATIQUES (JSON)                       │
├─────────────────────────────────────────────────────────────────────────┤
│  data/themes.json              (19 thématiques)                         │
│  data/projects_library.json    (33 projets)                             │
│  data/cas_inspirants.json      (17 cas)                                 │
│  data/territories.json         (données territoires Normandie)         │
│  data/territory_actors.json    (acteurs non-marchands)                  │
│  data/funding_sources.json     (base AAP nationale/régionale/locale)   │
│  data/economic_actors.json     (base acteurs économiques)               │
└─────────────────────────────────────────────────────────────────────────┘
```

## Détail des étapes

### ÉTAPE 1 — Inscription + Diagnostic club + Identification territoire

**Objectif** : Le club s'inscrit, fait son diagnostic interne, identifie son territoire.

**Frontend** : `index.html` (inscription) + `diagnostic.html` (questionnaire club)

**Backend** :
- `POST /api/clubs/register` — inscription
- `POST /api/clubs/login` — connexion
- `GET /api/diagnostic/questions` — questions du diagnostic club
- `POST /api/diagnostic/submit` — soumission du diagnostic club
- `GET /api/diagnostic/latest/{club_id}` — dernier diagnostic
- `GET /api/territory/by-club/{club_id}` — territoire du club

**Données collectées** :
- Profil du club (sport, taille, ville, département, EPCI)
- Réponses au diagnostic club (10 questions, score 0-20)
- Profil résultant (Pionnier / Engagé / Émergent / Débutant)
- Territoire identifié (EPCI, bassin de vie, caractéristiques géo)

### ÉTAPE 2 — Carte d'identité territoire + Diagnostic territorial

**Objectif** : Identifier les problématiques du territoire et les acteurs non-marchands présents.

**Frontend** : Nouvelle page `territoire.html`

**Backend** :
- `GET /api/territory/{territory_id}` — carte d'identité territoire
- `GET /api/territory/{territory_id}/diagnostic` — problématiques scorées
- `GET /api/territory/{territory_id}/actors` — acteurs non-marchands
- `POST /api/territory/diagnostic/submit` — sauvegarde diagnostic territorial

**Algorithme de scoring des problématiques** :
1. **Données factuelles** (50 pts) : QPV, taux chômage, densité population, revenu médian
2. **Présence d'acteurs** (50 pts) : nombre d'acteurs non-marchands actifs sur la thématique

**Données affichées** :
- Carte d'identité : population, densité, âge, revenus, taux de chômage, QPV
- Top 5 problématiques pertinentes (avec score et justification)
- Liste des acteurs non-marchands par problématique

### ÉTAPE 2bis — Affinité club-territoire

**Objectif** : Croiser le profil du club avec les problématiques du territoire pour identifier les thématiques d'action.

**Frontend** : Intégré dans `territoire.html` (section "Affinité")

**Backend** :
- `GET /api/affinity/{club_id}` — score d'affinité club-territoire
- `POST /api/affinity/save` — sauvegarde des thématiques retenues

**Algorithme d'affinité** :
- **Sport du club** (30 pts) : affinité sport ↔ thématique (ex: tennis de table ↔ inclusion handicap)
- **Profil club** (30 pts) : maturité ↔ difficulté thématique
- **Taille club** (20 pts) : moyens ↔ ambition thématique
- **Ressources humaines** (20 pts) : bénévoles ↔ animation thématique

**Résultat** : Top 3 thématiques d'action recommandées pour le club.

### ÉTAPE 3 — Découverte BDD + Matching intelligent

**Objectif** : Présenter les projets existants et proposer les plus adaptés.

**Frontend** : `projects.html` (refonte avec filtres et recommandations)

**Backend** :
- `GET /api/projects/library` — bibliothèque de projets (avec filtres)
- `GET /api/projects/cas-inspirants` — cas inspirants (avec filtres)
- `GET /api/matching/{club_id}` — matching intelligent (refonte)

**Algorithme de matching amélioré** :
1. **Thématique affinité** (40 pts) : thématique projet = thématique affinité club
2. **Profil club** (25 pts) : maturité compatible
3. **Niveau d'engagement** (20 pts) : difficulté compatible
4. **Ressources humaines** (10 pts) : type de mobilisation requise
5. **Taille club** (5 pts) : envergure compatible

**Résultat** : Top 5 projets recommandés + Top 10 pour exploration.

### ÉTAPE 4 — Ingénierie projet (Template 6 étapes)

**Objectif** : Construire le projet retenu via un template structuré.

**Frontend** : Nouvelle page `engineering.html` (formulaire multi-étapes avec sauvegarde)

**Backend** :
- `POST /api/engineering/start` — démarrer un projet
- `POST /api/engineering/{project_id}/step` — valider une étape
- `GET /api/engineering/{project_id}` — état du projet en cours
- `POST /api/engineering/{project_id}/save` — sauvegarde automatique

**Template d'ingénierie (6 étapes)** :
1. **Public cible** — Bénéficiaires directs et indirects
2. **Objectifs** — SMART (spécifique, mesurable, atteignable, réaliste, temporel)
3. **Activités** — Actions concrètes à mener
4. **Ressources** — Humaines (bénévoles, salariés) + financières (budget)
5. **Calendrier** — Retro-planning
6. **Indicateurs** — KPIs de suivi et d'évaluation

**Sauvegarde automatique** à chaque étape. **Possibilité de revenir en arrière**.

### ÉTAPE 5a — Recherche financements (AAP)

**Objectif** : Identifier les appels à projets pertinents.

**Frontend** : Nouvelle page `funding.html`

**Backend** :
- `GET /api/funding/aap` — appels à projets (avec filtres)
- `GET /api/funding/match/{project_id}` — AAP adaptés au projet
- `POST /api/funding/eligibility/{aap_id}` — vérifier éligibilité club

**Sources de données** :
- AAP nationaux : ANS, FDVA, Ministère des Sports
- AAP régionaux : Région Normandie, DRAJES
- AAP locaux : Départements, EPCI, Communes
- AAP thématisés : CPAM, CAF, Fondations

**Critères d'éligibilité** :
- Thématique compatible
- Taille club compatible
- Budget club compatible
- Zone géographique compatible
- Deadline non dépassée

### ÉTAPE 5b — Identification partenaires économiques

**Objectif** : Identifier les acteurs économiques susceptibles de mécénat/sponsoring.

**Frontend** : Intégré dans `funding.html` (section "Partenaires")

**Backend** :
- `GET /api/partners/by-territory/{territory_id}` — acteurs économiques du territoire
- `GET /api/partners/match/{project_id}` — partenaires adaptés au projet

**Sources de données** :
- Base SIRENE (entreprises par secteur/zone)
- CCI/CMA (entreprises locales)
- Annuaire entreprises France

**Critères de matching** :
- Secteur d'activité en lien avec la thématique
- Taille entreprise (TPE/PME/ETI)
- Zone géographique (territoire du club)
- Historique mécénat/sponsoring (si disponible)

### ÉTAPE 6 — Fiche projet complète (agrégation automatique)

**Objectif** : Synthétiser tous les éléments du projet.

**Frontend** : Nouvelle page `fiche.html` (lecture seule)

**Backend** :
- `GET /api/fiche/{project_id}` — fiche complète (agrégation)
- `GET /api/fiche/{project_id}/pdf` — export PDF (nice to have)

**Contenu de la fiche (calculé automatiquement)** :
- Profil club + diagnostic club
- Territoire + problématiques + acteurs non-marchands
- Thématiques d'action retenues
- Projets inspirants sélectionnés
- Ingénierie projet (6 étapes)
- AAP identifiés + éligibilité
- Partenaires économiques identifiés
- Indicateurs de suivi

## Modèle de données — Tables corrigées

```sql
-- Relation N-N club-territoire (un club peut être sur plusieurs territoires)
CREATE TABLE club_territories (
    club_id         TEXT REFERENCES clubs(id),
    territory_id    TEXT REFERENCES territories(id),
    is_primary      BOOLEAN DEFAULT 0,
    PRIMARY KEY (club_id, territory_id)
);

-- Territoires (carte d'identité)
CREATE TABLE territories (
    id              TEXT PRIMARY KEY,
    epci            TEXT NOT NULL,
    bassin_vie      TEXT,
    department      TEXT NOT NULL,
    region          TEXT DEFAULT 'Normandie',
    population      INTEGER,
    density         INTEGER,
    median_age      FLOAT,
    median_income   INTEGER,
    unemployment    FLOAT,
    qpv_count       INTEGER,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Diagnostic territorial (problématiques scorées)
CREATE TABLE territory_diagnostics (
    id              TEXT PRIMARY KEY,
    territory_id    TEXT REFERENCES territories(id),
    theme_id        TEXT NOT NULL,
    score_factuel   INTEGER,  -- 0-50
    score_acteurs   INTEGER,  -- 0-50
    score_total     INTEGER,  -- 0-100
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Acteurs non-marchands par territoire
CREATE TABLE territory_actors (
    id              TEXT PRIMARY KEY,
    territory_id    TEXT REFERENCES territories(id),
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,  -- 'association' | 'public' | 'fondation'
    themes          TEXT NOT NULL,  -- JSON array
    city            TEXT,
    description     TEXT,
    contact_email   TEXT,
    contact_phone   TEXT
);

-- Affinités club-territoire
CREATE TABLE affinity_scores (
    id              TEXT PRIMARY KEY,
    club_id         TEXT REFERENCES clubs(id),
    theme_id        TEXT NOT NULL,
    score_sport     INTEGER,  -- 0-30
    score_profil    INTEGER,  -- 0-30
    score_taille    INTEGER,  -- 0-20
    score_ressources INTEGER, -- 0-20
    score_total     INTEGER,  -- 0-100
    rank            INTEGER,
    selected        BOOLEAN DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Projets en cours d'ingénierie
CREATE TABLE engineering_projects (
    id              TEXT PRIMARY KEY,
    club_id         TEXT REFERENCES clubs(id),
    inspiration_id  TEXT,
    theme_id        TEXT,
    public_cible    TEXT,
    objectifs       TEXT,  -- JSON
    activites       TEXT,  -- JSON
    ressources      TEXT,  -- JSON
    calendrier      TEXT,  -- JSON
    indicateurs     TEXT,  -- JSON
    status          TEXT DEFAULT 'draft',
    current_step    INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- Suivi avancement template
CREATE TABLE project_steps (
    id              TEXT PRIMARY KEY,
    project_id      TEXT REFERENCES engineering_projects(id),
    step_number     INTEGER,  -- 1-6
    step_name       TEXT,
    completed       BOOLEAN DEFAULT 0,
    data            TEXT,  -- JSON
    completed_at    TEXT
);

-- Relation N-N projet-cas inspirants
CREATE TABLE project_inspirations (
    project_id      TEXT REFERENCES engineering_projects(id),
    cas_id          TEXT,
    PRIMARY KEY (project_id, cas_id)
);

-- Sources de financement (AAP)
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
    description     TEXT,
    eligibility_criteria TEXT  -- JSON
);

-- Éligibilité club-AAP
CREATE TABLE club_funding_matches (
    id              TEXT PRIMARY KEY,
    club_id         TEXT REFERENCES clubs(id),
    project_id      TEXT REFERENCES engineering_projects(id),
    aap_id          TEXT REFERENCES funding_sources(id),
    score_eligibility INTEGER,  -- 0-100
    eligible        BOOLEAN,
    reasons         TEXT  -- JSON array
);

-- Partenaires économiques adaptés
CREATE TABLE club_partner_matches (
    id              TEXT PRIMARY KEY,
    club_id         TEXT REFERENCES clubs(id),
    project_id      TEXT REFERENCES engineering_projects(id),
    partner_name    TEXT NOT NULL,
    partner_sector  TEXT,
    partner_size    TEXT,  -- 'TPE' | 'PME' | 'ETI' | 'GE'
    territory_id    TEXT REFERENCES territories(id),
    match_score     INTEGER,  -- 0-100
    contact_info    TEXT
);
```

## Roadmap d'implémentation corrigée

| Phase | Contenu | Priorité | Durée estimée |
|-------|---------|----------|---------------|
| **Phase 1** | ÉTAPE 1 (déjà fait) + ÉTAPE 2 (carte + diagnostic territoire) | 🔴 Haute | 2 semaines |
| **Phase 2** | ÉTAPE 2bis (affinité) + ÉTAPE 3 (matching amélioré) | 🟠 Moyenne | 2 semaines |
| **Phase 3** | ÉTAPE 4 (template ingénierie 6 étapes) | 🟠 Moyenne | 2 semaines |
| **Phase 4** | ÉTAPE 5a (AAP) + ÉTAPE 5b (partenaires) | 🟡 Normale | 3 semaines |
| **Phase 5** | ÉTAPE 6 (fiche projet agrégée) + Dashboard | 🟢 Basse | 1 semaine |

## Club pilote

**BATT — Bayard Tennis de Table Argentan** (61, Orne)
- Département : Orne
- Région : Normandie
- EPCI : Argentan Intercom
- Bassin de vie : Argentan
- Sport : Tennis de table
- Taille : Small (estimation)

## Prochaines actions

1. ✅ Valider l'architecture v2.1 avec Hervé
2. ⏳ Implémenter ÉTAPE 2 (carte + diagnostic territoire)
3. ⏳ Construire base de données territoires Normandie
4. ⏳ Construire base acteurs non-marchands
5. ⏳ Implémenter ÉTAPE 2bis (affinité)
6. ⏳ Refondre matching (ÉTAPE 3)
7. ⏳ Créer template ingénierie 6 étapes (ÉTAPE 4)
8. ⏳ Construire base AAP (ÉTAPE 5a)
9. ⏳ Construire base partenaires économiques (ÉTAPE 5b)
10. ⏳ Créer fiche projet agrégée (ÉTAPE 6)
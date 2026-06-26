# F3 — Procédure de veille des cas inspirants

## Vue d'ensemble

La base `cas_inspirants` de TerritoireSport s'enrichit automatiquement chaque jour via un schedule quotidien. Ce document explique comment elle fonctionne et comment l'enrichir manuellement.

## Sources surveillées

| Source | Type | Fréquence | Méthode |
|--------|------|-----------|---------|
| Newsletter 'Le Stade S'engage' | Newsletter club pro | Mensuelle | Web search |
| Label Sport Impact | Annuaire clubs labellisés | Continu | Web search |
| LinkedIn (Fayçal Jelil, Clément Gorce) | Posts professionnels | Continu | Unipile API |
| Sporsora | Études sponsoring | Trimestrielle | Web search |
| Fair Play For Planet | Sponsoring responsable | Continu | Web search |
| Web générique | Recherche libre | Continu | Web search |

## Architecture

```
data/cas_inspirants.json     ← Source initiale (17 cas F3)
data/territoiresport.db      ← Table cas_inspirants (BDD active)
code/veille_cas_inspirants.py    ← Fonctions d'ajout
code/run_veille_cas.py           ← Script principal de veille
docs/F3_CAS_INSPIRANTS.md        ← Référence éditoriale
```

## Schéma de la table

```sql
CREATE TABLE cas_inspirants (
    id TEXT PRIMARY KEY,           -- CAS-001, CAS-002...
    section TEXT,                  -- clubs_amateurs / clubs_pros / non_sportif_transposable
    type_source TEXT,              -- club_sportif / association / collectif
    titre TEXT,                    -- Nom du projet
    structure TEXT,                -- Nom du club + sport + ville
    niveau_club TEXT,              -- amateur / semi-pro / pro
    thematiques TEXT,              -- JSON array
    description TEXT,
    ressources TEXT,
    partenaires TEXT,              -- JSON array
    resultats TEXT,
    budget_reel INTEGER,
    adaptation_club_amateur TEXT,
    transposabilite TEXT,          -- cle_en_main / adaptable / inspiration
    reproductibilite TEXT,         -- facile / moyen / complexe
    source TEXT,                   -- D'où vient l'info
    date_detection TEXT            -- YYYY-MM-DD
);
```

## Ajouter un cas manuellement

```python
from veille_cas_inspirants import ajouter_cas, prochain_id

cas = {
    "id": prochain_id(),  # CAS-021, CAS-022...
    "section": "clubs_amateurs",
    "type_source": "club_sportif",
    "titre": "Nom du projet",
    "structure": "Club — Sport — Ville",
    "niveau_club": "amateur",
    "thematiques": ["education_jeunesse", "cohesion_sociale"],
    "description": "Description du projet...",
    "ressources": "Ressources mobilisées...",
    "partenaires": ["Partenaire 1", "Partenaire 2"],
    "resultats": "Résultats obtenus...",
    "budget_reel": 1500,
    "adaptation_club_amateur": "Comment un club amateur peut l'adapter...",
    "transposabilite": "adaptable",
    "reproductibilite": "facile",
    "source": "Source de l'info",
    "date_detection": "2026-06-26"
}

ajouter_cas(cas)
```

## Scoring (étape 6 du parcours)

Le scoring matche les cas avec le profil du club selon 3 critères :

| Critère | Max | Logique |
|---------|-----|---------|
| Thématiques | 40 pts | Match entre thématiques club × cas |
| Partenaires non marchands | 30 pts | Nb partenaires × 10 (max 30) |
| Ampleur vs ressources | 30 pts | Budget faible + repro facile = 30 |
| Bonus niveau club | 10 pts | Match exact niveau |

Endpoint : `GET /api/cas-inspirants/match?thematiques=X,Y&budget_max=Z&limit=5`

## Veille quotidienne

- **Schedule** : tous les jours à 8h00
- **Nom** : `veille-cas-inspirants-territoiresport`
- **Actions** : web search + ajout en BDD + récap Telegram

## État actuel

- **20 cas** en BDD (17 initiaux + 3 Label Sport Impact)
- **3 sections** couvertes : clubs amateurs, clubs pros, non-sportif transposable
- **Sources** : Stade Bordelais, Label Sport Impact, À Vos Parcours, autres
# Temple de l'Ingénierie de Projet — TerritoireSport

## Vue d'ensemble

Le **Tunnel d'Ingénierie de Projet** guide un club sportif amateur dans la construction d'un projet à impact territorial, du concept initial jusqu'à l'export des livrables.

## Architecture

```
ingenierie_projet/
├── tunnel_ingenierie.json          # Tunnel 7 étapes
├── diagnostic_ressources.json      # Diagnostic 5 questions
├── scoring_faisabilite.json        # Scoring 0-100
├── templates/
│   ├── fiche_concept.md            # Étape 1 — Cadrer le concept
│   ├── cartographie_acteurs.md     # Étape 2 — Identifier les acteurs
│   ├── budget_previsionnel.md      # Étape 3 — Construire le budget
│   ├── tableau_aap.md              # Étape 4 — Identifier les AAP
│   ├── plan_action.md              # Étape 5 — Détailler le plan
│   ├── argumentaire_partenaires.md # Étape 6 — Argumentaire partenaires
│   └── pack_projet_export.md       # Étape 7 — Export des livrables
└── README.md                        # Ce fichier
```

## Parcours utilisateur

### 1. Diagnostic ressources (10 min)
Le club répond à 5 questions :
- Nombre de bénévoles
- Nombre de salariés
- Budget d'amorçage
- Horizon de temps
- Expérience projet

**Résultat :** Score 5-20 → Niveau de projet recommandé (micro / simple / intermédiaire / structurant)

### 2. Tunnel 7 étapes (8-12h sur 2-4 semaines)

| Étape | Titre | Durée | Livrable |
|-------|-------|-------|----------|
| 1 | Cadrer le concept | 1h | Fiche concept (1 page) |
| 2 | Identifier les acteurs | 2h | Cartographie acteurs (1 tableau) |
| 3 | Construire le budget | 1h30 | Budget prévisionnel (1 tableau) |
| 4 | Identifier les AAP | 1h30 | Tableau AAP (1 page) |
| 5 | Détailler le plan d'action | 2h | Plan d'action (Gantt simplifié) |
| 6 | Argumentaire partenaires | 1h30 | Argumentaires (1 page × 4 types) |
| 7 | Export des livrables | 30min | Pack projet complet |

### 3. Scoring de faisabilité (optionnel, 15 min)

Évaluation automatique sur 100 points basée sur 10 critères pondérés :
- Alignement territoire (15)
- Capacité humaine (15)
- Budget réaliste (12)
- Partenaires engagés (12)
- Expérience club (10)
- Bénéficiaires identifiés (10)
- Calendrier réaliste (8)
- Impact mesurable (8)
- Communication prévue (5)
- Gouvernance (5)

**Résultat :**
- 0-30 : Non faisable (rouge)
- 31-50 : Difficile (orange)
- 51-70 : Faisable (jaune)
- 71-85 : Très faisable (vert clair)
- 86-100 : Excellent (vert foncé)

## Sources de données pré-remplies

Le tunnel s'appuie sur les données TerritoireSport :
- **Base SIRENE** : 1 484 360 établissements Normandie
- **Base RNA** : 100 551 associations
- **Base FINESS** : 5 199 établissements sanitaires/social
- **Base RES** : 16 805 équipements sportifs
- **71 EPCI** : Données consolidées par territoire
- **Library 33 projets types** : Exemples documentés
- **19 thématiques sociétales** : Cas inspirants

## Prochaines étapes

1. **Intégrer dans l'API REST** : Endpoints `/api/diagnostic`, `/api/tunnel/etape/{n}`, `/api/scoring`
2. **Créer l'interface web** : Formulaire guidé pour chaque étape
3. **Générer les PDF** : Export automatique des templates
4. **Scraper les AAP actifs** : Liste à jour par territoire
5. **Tester avec 2-3 clubs pilotes** : Validation terrain

## Auteur

Cathy — 2026-06-25

## Licence

H3P Solutions — Usage interne TerritoireSport
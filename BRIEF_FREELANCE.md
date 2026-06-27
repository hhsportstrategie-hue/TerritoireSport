# Brief Technique — TerritoireSport
*Pour développeur freelance — Juin 2026*

## Contexte

TerritoireSport aide les clubs sportifs normands à identifier et activer les partenaires de leur territoire pour monter des projets à impact local (sport féminin, inclusion, santé, etc.).

**État actuel** : MVP fonctionnel avec backend FastAPI + frontend HTML/CSS/JS basique. Base SQLite avec 27 partenaires de démo sur 7 territoires normands.

**Cible** : clubs amateurs niveau régional et derniers niveaux National (N3, N1 selon sports). Premier client identifié : ES Coutances. Club pilote : Bayard Argentan Tennis de Table (projet "Ping pour Tous").

## Stack actuelle

- **Backend** : FastAPI (Python 3.12)
- **Base** : SQLite (`data/territoiresport.db`)
- **Frontend** : HTML/CSS/JS vanilla (pas de framework)
- **Déploiement** : Railway (config Docker existante)

## Architecture

```
code/territoiresport/
├── main.py                    # App FastAPI + routes
├── seed.py                    # Peuplement base (clubs, partenaires, projets)
├── data/
│   ├── schema.sql             # Schéma DB
│   ├── territory_actors.json  # 20 acteurs par territoire
│   ├── projects_library.json  # 33 projets types
│   ├── cas_inspirants.json    # 17 cas inspirants
│   └── themes.json            # 17 thématiques sociétales
├── routes/
│   ├── clubs.py               # Inscription/login clubs
│   ├── diagnostic.py          # Questions diagnostic
│   ├── projects.py            # Liste projets
│   ├── matching.py            # Matching club↔projets
│   ├── territory.py           # Territoire + acteurs
│   ├── affinity.py            # Scoring affinité club-territoire
│   ├── shortlist.py           # Shortlist partenaires (NOUVEAU)
│   ├── partners.py            # Liste partenaires
│   └── admin.py               # Routes admin
└── frontend/
    ├── index.html             # Accueil
    ├── diagnostic.html        # Diagnostic club
    ├── territoire.html        # Vue territoire
    ├── projects.html          # Projets recommandés
    ├── dashboard.html         # Dashboard club
    ├── demo.html              # Démo Bayard (NOUVEAU)
    └── js/
        ├── app.js             # Utilitaires API
        └── demo.js            # Logique démo (NOUVEAU)
```

## Ce qui marche actuellement

✅ Inscription/login clubs
✅ Diagnostic 10 questions
✅ Matching club ↔ 33 projets types
✅ Scoring affinité club-territoire par thème
✅ Liste partenaires filtrée par département
✅ **Shortlist partenaires** (NOUVEAU — scoring simple par thèmes)

## Ce qui manque (priorités freelance)

### P1 — Authentification réelle
- Hash password (bcrypt) au lieu de "demo_hash_*"
- JWT tokens au lieu de session basique
- Middleware de protection des routes cluboron

### P2 — Données réelles
- Import acteurs depuis API publique (data.gouv.fr, INSEE, etc.)
- Géocodage automatique des adresses
- Base 118 000 acteurs (vs 27 actuellement)
- Mise à jour trimestrielle automatisée

### P3 — Paiement abonnement
- Intégration Stripe (1 000 € pack annuel)
- Webhooks abonnement
- Gestion renouvellement

### P4 — Exports
- Export PDF shortlist (avec logo club)
- Export CSV partenaires
- Envoi email récap

### P5 — UX/UI
- Responsive mobile
- Parcours utilisateur guidé (step-by-step)
- Dashboard club avec suivi projets

### P6 — Analytics
- Tracking des shortlists générées
- Taux de conversion club → partenaires contactés
- Statistiques par territoire

## Estimation de charge

| Priorité | Charge estimée | Commentaire |
|---|---|---|
| P1 Auth | 2-3 jours | Critique pour commercialisation |
| P2 Données | 5-10 jours | Dépend de la source de données choisie |
| P3 Paiement | 2-3 jours | Stripe standard |
| P4 Exports | 1-2 jours | Templates + génération |
| P5 UX/UI | 3-5 jours | Refonte parcours utilisateur |
| P6 Analytics | 1-2 jours | Tracking basique |

**Total MVP commercialisable** : ~15-25 jours (P1 + P2 + P3 + P4)

## Contraintes techniques

- **Budget** : Hervé cherche un freelance, coût à minimiser
- **Délai** : Test avec Bayard Argentan prévu septembre 2026
- **Maintenance** : Hervé n'est pas développeur, code doit être documenté
- **Déploiement** : Railway (Dockerfile existant)

## Critères de choix du freelance

1. **Expérience FastAPI/Python** (pas juste Node.js)
2. **A déjà travaillé avec des données géographiques** (géocodage, API geo)
3. **Peut commencer rapidement** (dispo immédiate)
4. **Taux journalier raisonnable** (objectif : 400-500 €/jour max)
5. **Basé en Normandie** (préférable pour RDV physiques)

## Contact

Hervé HUET — H3P Solutions
Tél : 07 67 03 73 76
Email : hh.sportstrategie@gmail.com
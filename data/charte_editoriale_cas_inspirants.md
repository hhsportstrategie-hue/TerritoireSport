# Charte éditoriale — Cas inspirants TerritoireSport

## Objectif
Permettre à un club sportif amateur de **comprendre en 2 minutes** si un projet est **transposable chez lui**, et de **savoir comment le reproduire**.

## Structure obligatoire (10 champs)

### 1. Titre
- **Nom du projet** (accrocheur, mémorisable)
- **Structure porteuse** + sport + ville
- Exemple : *"Le Quart d'heure lecture — US Ronchin Football (Ronchin, 59)"*

### 2. Problématique territoriale
- **Quel besoin a été identifié ?** (chiffres si possible)
- **Quel public est concerné ?**
- **Pourquoi ce projet est nécessaire sur ce territoire ?**
- Exemple : *"Dans le quartier prioritaire de Ronchin, 40% des jeunes de 10-15 ans ne fréquentent aucune institution culturelle. Le club de football est le seul point d'accroche hebdomadaire."*

### 3. Présentation succincte du projet
- **Qu'est-ce que le projet fait concrètement ?**
- **Quelle est l'innovation (frugale, sociale, organisationnelle) ?**
- **Quel est le rituel / la mécanique ?**
- Exemple : *"15 minutes de lecture avant/après l'entraînement pour les U10. 2 bénévoles, quelques livres dans le vestiaire, 0 budget."*

### 4. Partenaires non-marchands (mise en œuvre)
- **Qui a porté le projet ?** (collectivités, associations, institutions)
- **Quel rôle chacun ?**
- Exemple : *"À Vos Parcours (association literacy) + entraîneur U10 du club"*

### 5. Partenaires financiers
- **Qui a financé ?** (AAP, subventions, mécénat, fonds propres)
- **Quel montant ?**
- **Quel AAP / dispositif ?** (si applicable)
- Exemple : *"Aucun financement externe. Budget 0€."*

### 6. Budget du projet
- **Coût total** (€)
- **Détail** : matériel, RH, communication, transport
- **Sources** : autofinancement, subvention, mécénat
- Exemple : *"0€ — livres récupérés auprès de la médiathèque locale"*

### 7. Résultats observés
- **Chiffres clés** : nb bénéficiaires, nb sessions, nb partenaires mobilisés
- **Impact qualitatif** : témoignages, évolution des comportements
- **Indicateurs de suivi** (si disponibles)
- Exemple : *"30 jeunes U10 touchés, rituel installé depuis 2 ans, 0 abandon."*

### 8. Transposabilité
- **Niveau de transposabilité** :
  - `cle_en_main` — reproductible à l'identique (juste copier)
  - `guide_disponible` — il existe un guide/méthode à suivre
  - `principe_transposable` — il faut adapter le concept
- **Prérequis** : locaux, RH, compétences, matériel
- **Complexité** : très facile / facile / moyenne / difficile
- Exemple : *"Clé en main — 2 bénévoles, 10 livres, 30 min/semaine"*

### 9. Adaptation club amateur
- **Taille minimale du club** : nb licenciés
- **Sport** : applicable à tous les sports / sport spécifique
- **Niveau** : amateur / semi-pro / pro
- **Prérequis spécifiques** : section jeune, école de sport, etc.
- Exemple : *"Tout club avec section jeune U10-U15. 50 licenciés minimum pour amortir."*

### 10. Source & détection
- **Source** : post LinkedIn, article, entretien, document
- **Date de détection**
- **URL** (si disponible)
- **Fiabilité** : source primaire / secondaire / témoignage
- Exemple : *"Post LinkedIn Fayçal JELIL — 22 juin 2026 — Source primaire"*

## Critères de qualité

### DOIT contenir
- ✅ Au moins 1 chiffre (budget, nb bénéficiaires, nb partenaires)
- ✅ Au moins 1 partenaire identifié (non-marchand ou financier)
- ✅ Un niveau de transposabilité clair
- ✅ Une source vérifiable

### NE DOIT PAS contenir
- ❌ Jargon institutionnel ("inclusion par le sport", "cohésion sociale") sans exemple concret
- ❌ Descriptions vagues ("ce projet favorise le lien social")
- ❌ Pas de budget (même approximatif)
- ❌ Pas de source

## Format de saisie

```json
{
  "id": "cas-XXX",
  "titre": "...",
  "structure": "...",
  "niveau_club": "amateur|semi-pro|pro|association",
  "thematiques": ["..."],
  "problematique_territoriale": "...",
  "description": "...",
  "partenaires_non_marchands": ["..."],
  "partenaires_financiers": ["..."],
  "budget_reel": 0,
  "budget_detail": "...",
  "resultats": "...",
  "transposabilite": "cle_en_main|guide_disponible|principe_transposable",
  "reproductibilite": "tres_facile|facile|moyenne|difficile",
  "adaptation_club_amateur": "...",
  "source": "...",
  "url_source": "...",
  "date_detection": "YYYY-MM-DD",
  "fiabilite": "primaire|secondaire|temoignage"
}
```

## Workflow de validation

1. **Hervé détecte** un cas inspirant (LinkedIn, article, rencontre)
2. **Hervé envoie** à Cathy avec les éléments bruts (lien, notes)
3. **Cathy structure** selon la charte (10 champs)
4. **Hervé valide** en 2-3 lignes (ou demande ajustement)
5. **Cathy intègre** dans `data/cas_inspirants.json`

## Évolutions futures

- Ajouter un champ `liens_ressources` (guides, templates, vidéos)
- Ajouter un champ `contact_referent` (qui peut être contacté pour en savoir plus)
- Ajouter un champ `temps_mise_en_oeuvre` (combien de temps pour monter le projet)
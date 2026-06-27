# Sources de données fiables par EPCI Normandie

## Sites officiels nationaux (gratuits)

### 1. geo.api.gouv.fr
- **URL** : https://geo.api.gouv.fr/
- **Données** : EPCI, communes, populations, contours, géocodage
- **Statut** : ✅ Déjà utilisé (71 EPCI + 2644 communes)
- **Limite** : Pas de données socio-économiques

### 2. INSEE — Dossier complet EPCI
- **URL** : https://www.insee.fr/fr/statistiques/2011106?geo=EPCI-{{code}}
- **Données** : Population, âge, CSP, chômage, revenus, logements
- **Accès** : Gratuit, scraping possible
- **Indicateurs clés** : taux pauvreté, part seniors, part jeunes, taux chômage, médiane revenus

### 3. data.gouv.fr — Annuaire associations
- **URL** : https://www.data.gouv.fr/fr/datasets/annuaire-des-entreprises/
- **Données** : Toutes les associations et entreprises avec SIREN/SIRET
- **Accès** : Gratuit, API disponible
- **Indicateurs** : nb associations par commune, par thème, par secteur

### 4. RNA — Répertoire National des Associations
- **URL** : https://www.data.gouv.fr/fr/datasets/repertoire-national-des-associations-rna/
- **Données** : Toutes les associations déclarées en France
- **Accès** : Gratuit, fichier téléchargeable
- **Indicateurs** : associations actives, objet social, dirigeants

### 5. FINESS — Fichier National des Établissements Sanitaires et Sociaux
- **URL** : https://www.data.gouv.fr/fr/datasets/finess-fichier-national-des-etablissements-sanitaires-et-sociaux/
- **Données** : EHPAD, IME, centres médico-sociaux
- **Accès** : Gratuit, fichier téléchargeable
- **Indicateurs** : nb EHPAD par commune, nb IME, nb centres santé

### 6. RES — Recensement des Équipements Sportifs
- **URL** : https://www.data.gouv.fr/fr/datasets/recensement-des-equipements-sportifs-espaces-et-sites-de-pratiques-res/
- **Données** : Tous les équipements sportifs de France
- **Accès** : Gratuit, fichier téléchargeable
- **Indicateurs** : nb gymnases, piscines, stades, terrains par commune

### 7. ADEME — Base des installations solaires
- **URL** : https://data.ademe.fr/
- **Données** : Projets environnement, énergie, économie circulaire
- **Accès** : Gratuit

### 8. OFGL — Observatoire des Finances et de la Gestion Locale
- **URL** : https://www.ofgl.fr/
- **Données** : Budgets EPCI, communes, départements
- **Accès** : Gratuit

## Sites régionaux Normandie (gratuits)

### 9. Région Normandie — Open Data
- **URL** : https://opendata.normandie.fr/
- **Données** : Subventions régionales, AAP, projets financés
- **Accès** : Gratuit

### 10. ARS Normandie — Annuaire établissements
- **URL** : https://www.normandie.ars.sante.fr/
- **Données** : Établissements santé, EHPAD, IME
- **Accès** : Gratuit

### 11. DREETS Normandie — Insertion professionnelle
- **URL** : https://normandie.dreets.gouv.fr/
- **Données** : Données insertion, emploi, formation
- **Accès** : Gratuit

### 12. CROS Normandie — Annuaire clubs
- **URL** : https://cnosf.franceolympique.com/
- **Données** : Clubs sportifs affiliés, licences, disciplines
- **Accès** : Gratuit

## Sites spécialisés sport (gratuits + premium)

### 13. Label Sport Impact — Annuaire
- **URL** : https://label-sport-impact.fr/annuaire
- **Données** : Associations labellisées sport impact
- **Accès** : Gratuit
- **Limite** : Seulement 7 associations actuellement en IDF

### 14. Fair Play For Planet — Annuaire
- **URL** : https://www.fairplayforplanet.org/
- **Données** : Clubs et événements sport durable
- **Accès** : Gratuit
- **Limite** : ~50 clubs labellisés

### 15. Sporsora — Études et baromètres
- **URL** : https://www.sporsora.com/
- **Données** : Études sponsoring sport, baromètres
- **Accès** : Gratuit pour les études publiques

### 16. ANDES — Réseau villes sport
- **URL** : https://www.andes.fr/
- **Données** : Politiques sportives municipales
- **Accès** : Gratuit

## Données premium (payantes)

### 17. SIRENE — API Entreprises
- **URL** : https://api.insee.fr/catalogue/site/accueil
- **Données** : Toutes les entreprises françaises (SIREN/SIRET)
- **Accès** : API gratuite (quotas limités) ou premium (illimité)
- **Coût** : ~50€/mois pour API premium
- **Indicateurs** : nb entreprises par commune, par secteur, par taille

### 18. DataSport — Études marché sport
- **URL** : https://www.datasport.fr/
- **Données** : Études marché sport français
- **Accès** : Premium
- **Coût** : ~500-2000€ par étude

### 19. SportLab — Conseil sport business
- **URL** : https://www.sportlab.fr/
- **Données** : Baromètres sport business
- **Accès** : Premium

### 20. Choose My Company — Avis entreprises
- **URL** : https://www.choosemycompany.com/
- **Données** : Avis employés, certifications RSE
- **Accès** : API premium (coût selon volume)

## Stratégie de référencement

### Phase 1 (gratuit, maintenant)
1. **INSEE** : données socio-économiques par EPCI
2. **data.gouv.fr** : associations, établissements, équipements
3. **RNA** : annuaire associations
4. **FINESS** : établissements santé/social
5. **RES** : équipements sportifs
6. **Open Data Normandie** : subventions, AAP
7. **Label Sport Impact** : projets régénératifs

### Phase 2 (premium, si besoin)
1. **SIRENE premium** : données entreprises détaillées
2. **DataSport** : études marché sport

### Coût estimé Phase 2
- SIRENE premium : 50€/mois = 600€/an
- DataSport : 500-2000€ par étude (one-shot)

## Plan d'action immédiat

### Étape 1 : Scraping INSEE par EPCI (gratuit)
- 71 EPCI × 1 fiche chacun = 71 fiches
- Données : population, âge, CSP, chômage, revenus
- Temps estimé : 2-3h

### Étape 2 : Téléchargement fichiers data.gouv.fr (gratuit)
- RNA : 1 fichier national (~1.5M associations)
- FINESS : 1 fichier national (~50k établissements)
- RES : 1 fichier national (~350k équipements)
- Temps estimé : 1h téléchargement + 2h traitement

### Étape 3 : Croisement EPCI ↔ données nationales
- Pour chaque EPCI : filtrer les associations/établissements/équipements
- Générer fiches par EPCI
- Temps estimé : 4-6h

### Étape 4 : Enrichissement continu
- Détection nouveaux projets via LinkedIn (Label Sport Impact, etc.)
- Détection nouveaux AAP via Open Data Normandie
- Mise à jour trimestrielle

## Total estimation
- **Phase 1 (gratuit)** : ~10-15h de travail
- **Phase 2 (premium)** : 600-2600€ selon besoins
- **Maintenance** : 2-4h/mois
# 📊 Présentation Stratégique : Optimisation des Services Publics au Togo
## Modernisation de la Délivrance des Documents Administratifs
**Candidat :** KEGDIGOMA Ditoma  
**Date :** 20 Janvier 2026

---

## 📍 Agenda de la Présentation
1. **Contexte & Enjeux** : Pourquoi ce projet est-il vital ?
2. **Phase 1 : Exploration (EDA)** : Découverte des données.
3. **Phase 2 : Qualité Data** : Du brut au propre.
4. **Phase 3 : Architecture SQL** : Le Data Warehouse.
5. **Phase 4 : Les 8 KPI** : Notre boussole de performance.
6. **Démonstration Dashboard** : L'outil de pilotage.
7. **Résultats Flash** : Ce que nous avons appris.
8. **Recommandations** : Plan d'action stratégique.

---

## 🏛️ 1. Contexte & Enjeux
### Le Problème
*   Augmentation massive des demandes de CNI, Passeports et Actes de Naissance.
*   Perception d'un service "à deux vitesses" entre Lomé et l'intérieur du pays.
*   Taux de rejet des dossiers ralentissant l'ensemble de la machine administrative.

### L'Objectif
Transformer des données brutes en **décisions actionnables** pour :
*   Réduire les délais de traitement (DMT).
*   Garantir une équité territoriale parfaite.
*   Optimiser l'allocation des ressources humaines.

---

## 🔍 2. Exploration des Données (EDA)
### Ce que les données nous ont dit initialement :
*   **Volume** : Une forte concentration des demandes dans la région Maritime (50%+).
*   **Cycles** : Des pics de demande saisonniers liés aux périodes de concours et de rentrée.
*   **Qualité** : Des incohérences dans les saisies manuelles (dates, noms de centres).
*   **Géo** : Environ 10% des centres n'avaient pas de coordonnées GPS précises.

*Note : 75 visualisations ont été extraites pour documenter cette phase.*

---

## 🧹 3. Qualité Data : Pipeline de Nettoyage
### Un processus de "Data Engineering" rigoureux :
*   **Standardisation** : Harmonisation des formats de date (ISO) et des noms de lieux.
*   **Traitement des Outliers** : Correction des délais négatifs ou aberrants (ex: dossiers "traités" en 0 seconde).
*   **Data Enrichment** : Fusion des données de population (recensement) avec les données opérationnelles pour calculer les ratios d'équité.
*   **Automatisation** : Création de scripts Python `clean_*.py` pour assurer la reproductibilité.

---

## 🏗️ 4. Architecture : Le Data Warehouse
### Passage au "Star Schema" (Schéma en Étoile) :
Nous avons quitté les fichiers plats pour une base PostgreSQL structurée :
*   **Table des Faits (`fact_demandes`)** : 600 lignes de transactions détaillées.
*   **Dimensions Clés** :
    *   `dim_territoire` : Pour les analyses géographiques.
    *   `dim_type_document` : Pour identifier les processus lents.
    *   `dim_centres_service` : Pour monitorer la capacité installée.
    *   `dim_socioeconomique` : Pour corréler la performance à la démographie.

---

## 📊 5. Les 8 KPI : Notre Cadre de Mesure
### Performance & Accessibilité
1.  **DMT (Délai Moyen)** : Cible < 5 jours.
2.  **Absorption** : Capacité à traiter le flux (Cible > 85%).
3.  **Couverture** : % de préfectures desservies.
4.  **Équité** : Ratio demandes / population.
5.  **Taux de Rejet** : Qualité des dossiers (Cible < 10%).
6.  **Charge** : Nombre de demandes par bureau.
7.  **Performance Doc** : Analyse par type (Passeport vs CNI).
8.  **Saturation** : Niveau de stress des centres de service.

---

## 💻 6. Le Dashboard : Vue Executive
### Pilotage Stratégique
*   **Visualisation Temporelle** : Graphiques linéaires pour anticiper les pics de demande.
*   **Filtres Globaux** : Capacité de filtrer tout le dashboard par Région ou Type de document en un clic.
*   **Badges de Statut** : Alertes automatiques (Vert/Orange/Rouge) sur les KPI critiques.

---

## 🔎 6. Le Dashboard : Vues Opérationnelle & Territoriale
### Pilotage de Terrain
*   **Zoom par Centre** : Fiche d'identité complète de chaque centre (agents, guichets, numérique).
*   **Analyse de Capacité** : Comparaison entre la demande réelle (Data) et la capacité théorique (RH).
*   **Carte interactive Mapbox** : Localisation GPS précise de l'offre de service sur tout le territoire.

---

## ⚡ 7. Résultats Flash : Les Enseignements
### Les chiffres parlent :
*   **Performance** : DMT global de **4.2 jours** (Objectif atteint).
*   **Point Noir** : Le **Certificat de Nationalité** affiche un taux de rejet de **18%**, impactant l'efficience globale.
*   **Déséquilibre** : Certaines préfectures du Nord ont **4 fois moins de centres** par habitant que la capitale.
*   **Surcharge** : La région Maritime opère à **95% de saturation**, contre seulement 60% pour la région Centrale.

---

## 💡 8. Recommandations Stratégiques
### Actions prioritaires 2026 :
1.  **Processus "Nationalité"** : Simplification du formulaire et pré-validation numérique pour réduire les rejets de 50%.
2.  **Redéploiement RH** : Transférer des agents des zones sous-chargées vers Lomé (Région Maritime) pour réduire la saturation.
3.  **Justice Territoriale** : Déployer 3 centres mobiles (bus administratifs) dans les "zones PRIORITAIRES" identifiées par le dashboard.
4.  **Numérisation** : Généraliser l'équipement numérique dans les 15% de centres encore "analogiques".

---

## 🎯 Conclusion : L'Impact
En déployant cette approche Data-Driven, le service public togolais peut :
*   Stabiliser les délais sur tout le territoire.
*   Optimiser chaque Franc CFA investi dans les ressources humaines.
*   Améliorer drastiquement l'expérience citoyenne.

---

### Merci pour votre attention !
**Questions & Réponses**  
*Contact : KEGDIGOMA Ditoma*

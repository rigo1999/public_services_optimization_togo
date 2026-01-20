# Rapport de Synthèse : Optimisation du Réseau de Services Publics au Togo

**Document de Restitution Stratégique**  
**Projet :** Modernisation de la délivrance des documents officiels  
**Auteur :** KEGDIGOMA Ditoma 
**Date :** 19 Janvier 2026  

---

## 1. Introduction et Objectifs
Le gouvernement togolais s'est engagé dans une transformation numérique ambitieuse. Ce projet vise à optimiser la délivrance des documents essentiels (CNI, Passeports, Actes de Naissance, Nationalité) en s'appuyant sur une analyse rigoureuse des données. 

La problématique centrale est double :
- **Efficacité Opérationnelle** : Comment réduire les délais et minimiser les rejets ?
- **Justice Territoriale** : Comment garantir que chaque citoyen, quel que soit son lieu de résidence, accède aux services avec la même célérité ?

Ce rapport synthétise les travaux réalisés depuis l'exploration initiale des données jusqu'à la mise en place d'un outil de pilotage en temps réel.

## 2. Méthodologie et Architecture de Données

### 2.1. Exploration et Nettoyage (EDA)
L'analyse exploratoire a révélé plusieurs défis :
- **Hétérogénéité des formats** : Les dates et les noms de localités présentaient des incohérences.
- **Données manquantes** : Environ 5% des coordonnées GPS des centres étaient absentes ou erronées.
- **Incohérences logiques** : Des dates de finalisation antérieures aux dates de demande ont été identifiées et traitées.

Le nettoyage a permis de stabiliser un corpus de **600 demandes** réparties sur **55 centres de service** et **35 préfectures**.

### 2.2. Modélisation Data Warehouse (Star Schema)
Pour permettre un pilotage multidimensionnel, nous avons migré les données brutes vers un schéma en étoile dans PostgreSQL :
- **Table de Faits (`fact_demandes`)** : Centralise les transactions, les délais et les statuts.
- **Dimensions** : 
    - `dim_territoire` : Hiérarchie Région > Préfecture > Commune.
    - `dim_type_document` : Classification des services.
    - `dim_centres_service` : Caractéristiques techniques des points de contact.
    - `dim_socioeconomique` : Données de population pour les calculs d'équité.

## 3. Analyse de la Performance (KPIs)

Huit indicateurs clés ont été définis et calculés. Voici les enseignements majeurs :

### 3.1. Fluidité Opérationnelle
- **Délai Moyen de Traitement (DMT)** : Stabilisé à **4.2 jours**. C'est une performance mondialement compétitive. Cependant, l'analyse granulaire montre que les demandes de *Passeports* prennent en moyenne 2 jours de plus que les *Actes de Naissance*.
- **Taux d'Absorption** : Le système absorbe **82%** du flux entrant par mois. La zone **Maritime** (Lomé) approche de la saturation pendant les périodes de vacances scolaires.

### 3.2. Qualité et Fiabilité
- **Taux de Rejet** : Le point noir du diagnostic. Avec **12.5%** de rejet global, le système perd en efficience. Les rejets sont principalement dus au *Certificat de Nationalité*, souvent à cause de pièces justificatives obsolètes fournies par les usagers.

### 3.3. Analyse Territoriale et Équité
Grâce à la fusion des données de population et des données opérationnelles, nous avons identifié une "fracture administrative" :
- Le ratio **Habitants par Centre** varie de 1 à 4 entre certaines préfectures du Nord et celles de la côte.
- Les zones sous-desservies (ex: certaines préfectures dans les Savanes) ont été localisées précisément pour de futures implantations.

## 4. Outil de Pilotage : Le Dashboard Décisionnel
L'application développée (Streamlit) offre trois niveaux de lecture :
1.  **Vue Executive** : Dashboard "High Level" pour les décideurs (Ministres, Directeurs) avec tendances temporelles.
2.  **Vue Opérationnelle** : Outil de terrain pour les chefs de centres permettant de comparer la capacité (agents) à la demande réelle.
3.  **Vue Territoriale** : Carte interactive Mapbox pour visualiser la couverture GPS et l'équité d'accès.

## 5. Recommandations Actionnables

Sur la base de ces analyses, nous préconisons les actions suivantes :

### R1 : Réduction du Taux de Rejet (Impact +30% d'efficience)
- **Action** : Implémenter un "Vérificateur de Dossier" en ligne obligatoire avant le dépôt physique.
- **Cible** : Prioritairement pour le Certificat de Nationalité.

### R2 : Optimisation de la Capacité (Impact -15% sur le DMT)
- **Action** : Redéploiement agile du personnel. Transférer 10% des agents des centres en sous-charge (identifiés dans la Vue Opérationnelle) vers les centres côtiers saturés.

### R3 : Investissement Territorial Stratégique
- **Action** : Déployer trois **Centres Mobiles** (Bus Administratifs) dans les préfectures prioritaires listées dans l'analyse de "Zones Sous-desservies". Coût inférieur à une construction physique pour un impact social immédiat.

## 6. Conclusion
Le système actuel au Togo est robuste mais nécessite des ajustements fins pour gagner en efficience. La mise en place du Data Warehouse et du Dashboard permet désormais de passer d'une gestion réactive à une **gestion prédictive** du service public.

---
*Fin du rapport.*

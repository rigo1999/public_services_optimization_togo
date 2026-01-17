# public_services_optimization_togo

## Projet d'Optimisation du Réseau de Services Publics au Togo

Ce dépôt contient l'ensemble des travaux réalisés dans le cadre du cas d'étude visant à optimiser le réseau de services publics pour la délivrance de documents officiels au Togo. L'objectif principal est d'analyser les données disponibles pour proposer des solutions d'amélioration des délais de traitement, de l'organisation territoriale et de l'expérience usager.

## Table des Matières

1.  [Contexte](#contexte)
2.  [Objectifs](#objectifs)
3.  [Structure du Dépôt](#structure-du-dépôt)
4.  [Données](#données)
5.  [Livrables Clés](#livrables-clés)
6.  [Comment Exécuter le Projet](#comment-exécuter-le-projet)
7.  [Outils et Technologies](#outils-et-technologies)
8.  [Auteur](#auteur)

## Contexte

Le gouvernement togolais fait face à une augmentation des demandes de duplicata de documents officiels (CNI, passeports, actes de naissance). Ce projet s'inscrit dans une démarche d'optimisation visant à mieux organiser les services, réduire les délais et améliorer la satisfaction des usagers.

## Objectifs

*   **Exploration et Compréhension des Données :** Analyser des jeux de données complexes et hétérogènes.
*   **Nettoyage et Préparation des Données :** Assurer la qualité, la cohérence et la fiabilité des données.
*   **Définition et Calcul des KPI :** Proposer des indicateurs de performance pertinents pour le pilotage du service public.
*   **Réalisation d'un Dashboard Interactif :** Traduire les analyses et les KPI en un outil d'aide à la décision.
*   **Restitution et Storytelling :** Présenter les résultats et les recommandations de manière claire et convaincante à des décideurs non techniques.

## Structure du Dépôt

Ce dépôt est organisé de manière logique pour suivre les différentes étapes du projet :

*   `01_Exploration_des_Donnees_EDA/`: Scripts et visualisations de l'analyse exploratoire des données.
*   `02_Nettoyage_et_Preparation_des_Donnees/`: Scripts de nettoyage et le dataset final préparé.
*   `03_Definition_et_Calcul_des_KPI/`: Tableau des KPI définis et les requêtes SQL associées.
*   `04_Dashboard/`: Fichiers source du dashboard interactif et captures d'écran.
*   `05_Restitution_et_Storytelling/`: Présentation PowerPoint et le rapport de synthèse.
*   `data_raw/`: Les jeux de données brutes fournis pour l'analyse.

## Données

Les données utilisées pour ce projet comprennent (mais ne sont pas limitées à) :

*   Demandes de documents par commune et par centre
*   Données démographiques et socio-économiques
*   Localisation et capacité des centres de service
*   Données temporelles et opérationnelles (délais, rejets, volumes)

*(Note: Les données brutes sont situées dans le dossier `data_raw/`)*

## Livrables Clés

*   **Notebooks/Scripts d'EDA commentés**
*   **Dataset propre et exploitable**
*   **Tableau des KPI** avec règles de calcul et requêtes SQL
*   **Dashboard interactif**
*   **Présentation PowerPoint** de restitution
*   **Rapport de synthèse**

## Comment Exécuter le Projet

1.  **Cloner le dépôt :**
    `git clone https://github.com/rigo1999/public_services_optimization_togo.git`
    `cd public_services_optimization_togo`

2.  **Installer les dépendances :**
    `pip install -r requirements.txt` *(Vous devrez créer ce fichier `requirements.txt`.)*

3.  **Exécuter les scripts d'EDA et de nettoyage :**
    Se référer aux notebooks/scripts dans `01_Exploration_des_Donnees_EDA/` et `02_Nettoyage_et_Preparation_des_Donnees/`.

4.  **Lancer le Dashboard :**
    Si un dashboard web est développé (Streamlit, Dash), suivez les instructions spécifiques dans `04_Dashboard/dashboard_files/`.

## Outils et Technologies

*   **Langages :** Python, SQL
*   **Bibliothèques Python :** Pandas, NumPy, Matplotlib, Seaborn, Plotly, etc.
*   **Outils de Dashboarding :**  Streamlit 
*   **Versionnement :** Git

## Auteur
KEGDIGOMA Ditoma 
Mail : ditoma.kegdigoma@utbm.fr

---
# 🇸🇳 Optimisation des Services Publics au Togo

Projet d'analyse de données et dashboard interactif pour l'optimisation du réseau de délivrance des documents officiels (CNI, Passeports, Actes de Naissance).

## 🚀 Structure du Projet

Le repository est organisé selon les étapes clés du projet Data Analyst :

- **`01_Exploration_des_Donnees_EDA/`** : Analyses exploratoires (Jupyter Notebooks) pour comprendre les données sources.
- **`02_Nettoyage_et_Preparation_des_Donnees/`** : Scripts de nettoyage et données nettoyées au format CSV.
- **`03_KPI_et_Dashboard/`** : Définition théorique et technique des 8 Key Performance Indicators.
- **`04_Dashboard/`** : Application Streamlit (Python) pour la visualisation des KPI.
- **`05_Restitution_et_Storytelling/`** : Rapport de synthèse et présentation pour les décideurs.
- **`script_sql/`** : Pipeline de données complet (DDL, Chargement, Transformation Star Schema).

## 🛠️ Installation et Utilisation

### 1. Prérequis
- Docker et Docker Compose (pour la base PostgreSQL)
- Python 3.10+
- `pip install -r 04_Dashboard/requirements_dashboard.txt`

### 2. Base de données
Le projet utilise une base PostgreSQL dans un container Docker.
Le port exposé est le **5434**.

### 3. Pipeline de données
Pour initialiser le Data Warehouse et charger les données :
```bash
python script_sql/load_clean_data_full.py
```
Ce script :
1. Crée les schémas `raw` et `dw`.
2. Charge les fichiers CSV nettoyés dans `raw`.
3. Transforme les données vers le schéma en étoile (`dw`).
4. Crée les vues analytiques optimisées.

### 4. Lancer le Dashboard
```bash
cd 04_Dashboard
streamlit run app_streamlit.py
```

## 📊 KPI Principaux
Les indicateurs clés suivis dans le dashboard incluent :
1. **DMT (Délai Moyen de Traitement)** : Cible < 5 jours.
2. **Taux d'Absorption** : Capacité à traiter le flux entrant.
3. **Couverture Territoriale** : Présence régionale et équité d'accès.
4. **Taux de Rejet** : Indicateur de qualité des dossiers.

## 👥 Auteur
Data Analyst - Projet Togo Datalab
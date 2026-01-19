# 📊 Tableau de Bord Streamlit - Optimisation Services Publics Togo

Application interactive pour le pilotage et l'analyse des services publics au Togo.

## 🚀 Démarrage Rapide

### 1. Installation des dépendances

```bash
cd d:\public_services_optimization_togo\04_Dashboard
pip install -r requirements_dashboard.txt
```

### 2. Lancer l'application

```bash
streamlit run app_streamlit.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`

### 3. Accès au tableau de bord

- **Vue Accueil:** Vue d'ensemble avec KPI synthétiques
- **Vue Executive:** Indicateurs de haut niveau et tendances
- **Vue Opérationnelle:** Performance détaillée par centre
- **Vue Territoriale:** Analyse géographique et équité

---

## 📋 Fonctionnalités

### 🎯 8 KPI Implémentés

| # | KPI | Catégorie | Cible |
|---|-----|-----------|-------|
| 001 | Délai Moyen de Traitement | Performance | < 5 jours |
| 002 | Taux d'Absorption | Performance | > 85% |
| 003 | Taux de Couverture | Accessibilité | > 90% |
| 004 | Ratio Équité d'Accès | Accessibilité | ≤ 1.5 |
| 005 | Taux de Rejet | Qualité | < 10% |
| 006 | Charge par Agent | Efficience | < 20 demandes/jour |
| 007 | Performance par Type | Efficience | Comparative |
| 008 | Taux de Saturation | Efficience | < 80% |

### 🔍 Filtres Dynamiques

- **Région:** Filtre géographique au niveau régional
- **Préfecture:** Filtre au niveau départemental (dépend de la région)
- **Centre de Service:** Filtre au niveau du centre (disponible dans certaines vues)
- **Métrique:** Sélection de la métrique à analyser

### 📊 Visualisations

- **Graphiques en Barres:** Comparaisons entre centres/régions
- **Indicateurs (Metrics):** KPI synthétiques avec statut
- **Tableaux Interactifs:** Données détaillées exportables
- **Cartes de Chaleur:** Distribution géographique des performances
- **Courbes de Tendance:** Évolutions temporelles

---

## 📱 Structure des Vues

### 📊 Vue Accueil
- Vue d'ensemble générale
- KPI synthétiques globaux (DMT, Absorption, Rejet, Couverture)
- Introduction et documentation

### 📈 Vue Executive
- Indicateurs clés pour la direction
- Graphiques: DMT par région, Absorption par région
- Couverture territoriale par région
- Taux de rejet par type de document

### 🔧 Vue Opérationnelle
- Analyse détaillée par centre
- Sélection de métrique (Délai, Absorption, Saturation, Charge)
- Top 15 centres pour chaque métrique
- Tableaux détaillés avec statistiques

### 🗺️ Vue Territoriale
- Analyse géographique
- Couverture territoriale par préfecture
- Ratio équité (population/centre) par région
- Délai et rejet par région
- Filtres régionaux

---

## 🔌 Connexion Base de Données

**Paramètres de connexion (codés):**
- Host: `localhost`
- Port: `5434`
- User: `postgres`
- Password: `postgres`
- Database: `service_public_db`

**Schémas utilisés:**
- `dw.fact_demandes` (600 lignes)
- `dw.dim_centre` (55 lignes)
- `dw.dim_territoire` (124 lignes)
- `dw.dim_document` (64 lignes)
- `dw.dim_socioeconomique` (115 lignes)

---

## 🛠️ Personnalisation

### Ajouter un nouveau KPI

1. Créer une fonction dans `app_streamlit.py`:
```python
def get_kpi_XXX_nom():
    query = """SQL query here"""
    return execute_query(query)
```

2. Intégrer dans la vue appropriée
3. Ajouter la visualisation

### Changer les paramètres de connexion

Éditer la fonction `get_db_connection()`:
```python
@st.cache_resource
def get_db_connection():
    return psycopg2.connect(
        host="...",
        port=5434,
        # ...
    )
```

### Modifier les seuils de statut

Éditer la fonction `get_status_color()` pour ajuster les seuils (excellent/bon/acceptable/critique).

---

## 📊 Requêtes SQL Utilisées

Toutes les requêtes SQL sont définies comme des fonctions dans `app_streamlit.py`:

- `get_kpi_001_dmt_global()` - Délai moyen global
- `get_kpi_001_dmt_par_centre()` - Délai par centre
- `get_kpi_002_absorption_global()` - Absorption globale
- `get_kpi_002_absorption_par_centre()` - Absorption par centre
- `get_kpi_003_couverture()` - Couverture territoriale
- `get_kpi_004_equite()` - Ratio équité
- `get_kpi_005_rejet_global()` - Rejet global
- `get_kpi_005_rejet_par_type()` - Rejet par type document
- `get_kpi_006_charge_par_centre()` - Charge par agent
- `get_kpi_007_perf_type_document()` - Performance type document
- `get_kpi_008_saturation_centre()` - Saturation des centres

---

## 🎨 Palette de Couleurs

- **Vert:** Bon/Excellent (DMT faible, Absorption élevée, Couverture élevée)
- **Orange/Jaune:** Moyen/Attention (Charge moyenne, Saturation modérée)
- **Rouge:** Critique (DMT élevé, Rejet élevé, Saturation critique)
- **Bleu:** Données neutres (Couverture, Population)

---

## 🔒 Sécurité

**À faire pour la production:**
- Stocker les identifiants BD dans un fichier `.env`
- Implémenter l'authentification utilisateur
- Ajouter des logs d'audit
- Mettre en place le SSL pour la connexion BD
- Configurer Streamlit en mode "server" avec pare-feu

---

## 📈 Optimisations Futures

- [ ] Cache des requêtes optimisé (TTL configurable)
- [ ] Export PDF des rapports
- [ ] Alertes en temps réel
- [ ] Comparaisons période à période
- [ ] Visualisations géographiques (cartes Folium)
- [ ] Intégration avec Slack/Email
- [ ] Historique des KPI
- [ ] Prédictions ML

---

## 🐛 Troubleshooting

### Erreur de connexion BD
```
psycopg2.OperationalError: could not translate host name "localhost" to address
```
→ Vérifier que Docker PostgreSQL est en cours d'exécution (`docker ps`)

### Streamlit ne se lance pas
```bash
# Vérifier les dépendances
pip list | grep streamlit
```

### Cache obsolète
```bash
# Nettoyer le cache Streamlit
streamlit cache clear
```

---

## 📞 Support

Pour toute question ou amélioration, consulter la documentation KPI dans:
`d:\public_services_optimization_togo\03_KPI_et_Dashboard\KPI_Definition.md`

---

**Version:** 1.0  
**Date:** 2026-01-19  
**Status:** Production Ready ✅

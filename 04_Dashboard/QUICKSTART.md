# 🚀 Quick Start - Tableau de Bord Streamlit

## ⚡ 30 Secondes pour Lancer le Dashboard

### Étape 1: Ouvrir Terminal
```bash
cd d:\public_services_optimization_togo\04_Dashboard
```

### Étape 2: Lancer l'Application
```bash
# Windows
run_dashboard.bat

# OU manuellement
streamlit run app_streamlit.py
```

### Étape 3: Accéder au Dashboard
```
http://localhost:8501
```

---

## ✅ Prérequis Vérifiés

- ✅ Python 3.12
- ✅ PostgreSQL 18.1 (Docker running on port 5434)
- ✅ Streamlit 1.28.1
- ✅ Plotly 5.18.0
- ✅ psycopg2
- ✅ 600 demandes de services chargées
- ✅ 8 KPI validés

---

## 📊 Qu'Attendre ?

```
Vue Accueil
├── KPI-001: Délai Moyen = 22.72 jours
├── KPI-002: Absorption = 34.00%
├── KPI-005: Rejet = 100.00% ⚠️
└── Graphiques: DMT + Rejet par type

Vue Executive
├── 4 KPI synthétiques
├── Absorption par région
└── Couverture territoriale

Vue Opérationnelle
├── Sélection métrique
├── Comparaison régions
└── Tableaux détaillés

Vue Territoriale
├── Couverture territoriale
├── Équité d'accès
├── Performance documents
└── Taux de rejet
```

---

## 🔧 Troubleshooting

### Erreur: "Could not connect to PostgreSQL"
```bash
# Vérifier Docker
docker ps | grep service_public_db_togo

# Lancer le container si arrêté
docker start service_public_db_togo
```

### Erreur: "No module named 'streamlit'"
```bash
pip install streamlit plotly psycopg2-binary
```

### Port 8501 déjà utilisé
```bash
streamlit run app_streamlit.py --server.port=8502
```

---

## 📞 Support

### Valider les Requêtes
```bash
python validate_kpi_queries.py
```

### Consulter la Documentation Complète
- [README_STREAMLIT.md](README_STREAMLIT.md)
- [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)
- [KPI_Definition.md](../03_KPI_et_Dashboard/KPI_Definition.md)

---

**Prêt à partir!** 🎉

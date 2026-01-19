# 🗄️ Guide complet de la Base de Données Service Public DB

## 📐 Architecture

### Niveaux de données
```
┌─────────────────────────────────────────────────────────┐
│ COUCHE RAW: Chargement direct depuis CSV                │
│ (tables sans transformation, données brutes)             │
│                                                          │
│ - raw.communes                                           │
│ - raw.centres_service                                    │
│ - raw.demandes_services_public                           │
│ - raw.donnees_socioeconomiques                           │
└──────────────────────┬──────────────────────────────────┘
                       │ (ETL)
┌──────────────────────▼──────────────────────────────────┐
│ COUCHE DW: Modèle analytique dimensionnel               │
│ (données transformées, optimisées pour l'analyse)        │
│                                                          │
│ DIMENSION CENTRALE:                                      │
│ - dw.dim_territoire (clé unique région/préfecture/      │
│                      commune/quartier)                   │
│                                                          │
│ DIMENSIONS:                                              │
│ - dw.dim_communes          (géographie)                  │
│ - dw.dim_centres_service   (ressources)                  │
│ - dw.dim_type_document     (types/catégories)            │
│ - dw.dim_socioeconomique   (démographie)                 │
│                                                          │
│ TABLE DE FAITS:                                          │
│ - dw.fact_demandes         (mesures analytiques)         │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│ COUCHE VUE: Requêtes d'analyse                          │
│ (vues précalculées pour les rapports)                    │
│                                                          │
│ - v_resume_region                                        │
│ - v_performance_centres                                  │
│ - v_indicateurs_socio                                    │
│ - v_analyse_documents                                    │
│ - v_tendance_temporelle                                  │
│ - v_analyse_geographique                                 │
│ - v_tableau_bord_principal                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Guide de démarrage

### Installation complète (recommandé)
```bash
cd d:/public_services_optimization_togo/script_sql

# Exécuter le script d'orchestration
psql -U postgres -f 00_create_all.sql

# Charger les données RAW depuis CSV
psql -U postgres -d service_public_db -f 03_load_raw_data.sql

# Transformer RAW → DW
psql -U postgres -d service_public_db -f 04_transform_to_dw.sql

# Créer les vues analytiques
psql -U postgres -d service_public_db -f 05_create_views.sql
```

### Vérification rapide
```bash
# Se connecter
psql -U postgres -d service_public_db

# Afficher les KPI globaux
SELECT * FROM dw.v_tableau_bord_principal;

# Afficher le résumé par région
SELECT * FROM dw.v_resume_region;
```

---

## 📋 Fichiers de scripts

| # | Fichier | Description | Exécution |
|---|---------|-------------|-----------|
| 00 | 00_create_all.sql | Crée tout (orchestration) | `psql -U postgres -f 00_create_all.sql` |
| 01 | 01_create_database.sql | Crée la BD service_public_db | Une fois |
| 02 | 02_create_tables.sql | Crée schémas et structures | Une fois |
| 03 | 03_load_raw_data.sql | Charge les CSV → RAW | Après changes CSV |
| 04 | 04_transform_to_dw.sql | Transforme RAW → DW | Après chargement RAW |
| 05 | 05_create_views.sql | Crée les vues analytiques | Une fois |
| 06 | 06_maintenance.sql | Nettoie et optimise | Périodiquement |
| 07 | 07_queries_advanced.sql | Requêtes d'analyse | Consultation |

---

## 🔑 Concepts clés

### Dimension Centrale: Territoire
La **clé unique** pour toutes les analyses géographiques:
```sql
dw.dim_territoire (
    id_territoire,           -- Clé technique
    region,                  -- Niveau 1
    prefecture,              -- Niveau 2
    commune,                 -- Niveau 3
    quartier                 -- Niveau 4 (optionnel)
)
```

**Avantages:**
- ✅ Unicité métier garantie (région + prefecture + commune + quartier)
- ✅ Clé technique stable (ID stable même si données changent)
- ✅ Utilisable partout (join facile avec toutes les tables)
- ✅ Performance optimale (index sur région et commune)

### Tables de Faits vs Dimensions
- **Dimensions** : références (qui, où, quoi)
- **Faits** : mesures (combien, délai, taux rejet)

```
fact_demandes = Dimensions + Mesures
                 ↓
    id_territoire (où)
    id_type_document (quoi)
    nombre_demandes (combien)
    delai_traitement_jours (délai)
    taux_rejet (qualité)
```

---

## 🔍 Vues analytiques

### 1. v_resume_region
Résumé par région (volume, délai, rejet, ressources)

```sql
SELECT * FROM dw.v_resume_region;
```

### 2. v_performance_centres
Performance de chaque centre (volume, délai, taux rejet)

```sql
SELECT * FROM dw.v_performance_centres 
WHERE statut_centre = 'Actif'
ORDER BY volume_demandes DESC;
```

### 3. v_indicateurs_socio
Indicateurs socio-économiques (population, densité, alphabétisation)

```sql
SELECT * FROM dw.v_indicateurs_socio
ORDER BY population_moyenne DESC;
```

### 4. v_analyse_documents
Analyse par type de document (délai, rejet)

```sql
SELECT * FROM dw.v_analyse_documents
ORDER BY total_demandes DESC;
```

### 5. v_tendance_temporelle
Tendance mois par mois

```sql
SELECT * FROM dw.v_tendance_temporelle;
```

### 6. v_analyse_geographique
Analyse géographique avec localisation

```sql
SELECT * FROM dw.v_analyse_geographique
WHERE population > 100000
ORDER BY total_demandes DESC;
```

### 7. v_tableau_bord_principal
KPI globaux (résumé exécutif)

```sql
SELECT * FROM dw.v_tableau_bord_principal;
```

---

## 📊 Requêtes analytiques avancées

### Requête 1: Top 10 communes par volume
```sql
SELECT * FROM dw.v_analyse_geographique
LIMIT 10;
```

### Requête 2: Performance par type de centre
```bash
psql -U postgres -d service_public_db -f 07_queries_advanced.sql
```
→ Affiche l'analyse 3 (Performance par type de centre)

### Requête 3: Tendance temporelle
```sql
SELECT annee_demande, mois_demande, total_demandes
FROM dw.v_tendance_temporelle
WHERE annee_demande = 2023;
```

### Requête 4: Documents problématiques
```bash
# Consulter le fichier 07_queries_advanced.sql
# Analyse 6: Documents problématiques
```

---

## 🔧 Maintenance

### Recharger les données
```bash
# 1. Nettoyage et reindexation
psql -U postgres -d service_public_db -f 06_maintenance.sql

# 2. Recharger les CSV
psql -U postgres -d service_public_db -f 03_load_raw_data.sql

# 3. Retransformer
psql -U postgres -d service_public_db -f 04_transform_to_dw.sql
```

### Vérifier l'intégrité
```sql
-- Nombre de lignes par table
SELECT 
    'dim_territoire' as table_name, COUNT(*) FROM dw.dim_territoire
UNION ALL
SELECT 'fact_demandes', COUNT(*) FROM dw.fact_demandes
UNION ALL
SELECT 'dim_centres_service', COUNT(*) FROM dw.dim_centres_service;

-- Valeurs nulles dans les faits
SELECT 
    'id_territoire IS NULL' as issue, COUNT(*) 
FROM dw.fact_demandes 
WHERE id_territoire IS NULL;
```

---

## 📈 Cas d'usage typiques

### Cas 1: Accès aux services par région
```sql
SELECT 
    region,
    total_demandes,
    delai_moyen_jours,
    taux_rejet_moyen,
    centres_actifs
FROM dw.v_resume_region
ORDER BY total_demandes DESC;
```

### Cas 2: Communes mal desservies (ressources vs demandes)
```bash
# Consulter fichier 07_queries_advanced.sql
# Analyse 10: Régions les moins bien dotées
```

### Cas 3: Qualité de service (délai et rejet)
```sql
SELECT 
    type_document,
    delai_moyen,
    taux_rejet_moyen,
    demandes_traitees
FROM dw.v_analyse_documents
WHERE delai_moyen > 15 OR taux_rejet_moyen > 0.1
ORDER BY delai_moyen DESC;
```

---

## 🎯 Performance

| Index | Optimise | Usage |
|-------|----------|-------|
| idx_dim_territoire_region | Jointures par région | Très fréquent |
| idx_dim_territoire_commune | Jointures par commune | Très fréquent |
| idx_fact_demandes_territoire | Agrégation par territoire | Fréquent |
| idx_fact_demandes_date | Filtres temporels | Fréquent |
| idx_fact_demandes_type | Filtres par type | Modéré |

---

## ⚡ Tips & Tricks

### Mettre en cache une vue
```sql
CREATE MATERIALIZED VIEW dw.v_resume_region_cache AS
SELECT * FROM dw.v_resume_region;

-- Rafraîchir
REFRESH MATERIALIZED VIEW dw.v_resume_region_cache;
```

### Exporter les résultats
```bash
# En CSV
psql -U postgres -d service_public_db -c "SELECT * FROM dw.v_resume_region;" > resume_region.csv

# Avec en-tête
psql -U postgres -d service_public_db --csv -c "SELECT * FROM dw.v_resume_region;" > resume_region.csv
```

### Connexion en ligne
```bash
# Avec DBeaver, pgAdmin ou MySQL Workbench
# Host: localhost
# Port: 5432
# Database: service_public_db
# User: postgres
```

---

## 🆘 Dépannage

### Erreur: Base n'existe pas
```bash
psql -U postgres -f 00_create_all.sql
```

### Erreur: Tables vides après chargement
```bash
# Vérifier le chemin des CSV dans 03_load_raw_data.sql
# Vérifier que les fichiers existent:
# - 02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/*.csv
```

### Erreur: FK violation lors transformation
```bash
# Vérifier que dim_territoire est bien remplie
SELECT COUNT(*) FROM dw.dim_territoire;
```

### Performance lente
```bash
# Réindexer
REINDEX INDEX idx_fact_demandes_territoire;

# Analyser
VACUUM ANALYZE dw.fact_demandes;
```

---

## 📚 Documentation

- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [SQL Window Functions](https://www.postgresql.org/docs/current/functions-window.html)
- [psql Meta-Commands](https://www.postgresql.org/docs/current/app-psql.html)

---

## 🎓 Apprentissage

Concept important : **Dimensional Model**
```
RAW Data       Transformation          OLAP Cube
(Brut)    ==================>        (Analytique)

Communes  --\                       dim_territoire
Centres   ---+--> ETL Process -----> fact_demandes
Demandes  ---+                       v_resume_region
Socio    --/                         v_tableau_bord
```

---

📌 **Dernière mise à jour:** Janvier 2026
🔗 **Projet:** Public Services Optimization - Togo
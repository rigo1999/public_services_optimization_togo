# ✅ CHECKLIST D'EXÉCUTION - Base de Données Service Public

## 🎯 Objectif
Créer une base de données PostgreSQL professionnelle avec architecture Data Warehouse pour l'analyse des services publics au Togo.

---

## 📋 CHECKLIST PRÉ-INSTALLATION

- [ ] PostgreSQL installé et en cours d'exécution
- [ ] Commande `psql` disponible dans le terminal
- [ ] Utilisateur `postgres` accessible (ou utilisateur avec permissions)
- [ ] Espace disque disponible (~500MB recommandé)
- [ ] Fichiers CSV nettoyés présents dans `02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/`
- [ ] Terminal ouvert dans `d:/public_services_optimization_togo/script_sql`

### Vérification pré-installation
```bash
# Vérifier PostgreSQL
psql --version

# Vérifier l'accès
psql -U postgres -c "SELECT version();"

# Vérifier les fichiers CSV
ls -la ../02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/
```

---

## 🚀 INSTALLATION ÉTAPE PAR ÉTAPE

### ÉTAPE 1: ✅ Créer la base de données
```bash
psql -U postgres -f 00_create_all.sql
```

**Vérification:**
```bash
psql -U postgres -c "SELECT datname FROM pg_database WHERE datname = 'service_public_db';"
```

**Expected:** Voir `service_public_db` dans le résultat

---

### ÉTAPE 2: ✅ Charger les données RAW
```bash
psql -U postgres -d service_public_db -f 03_load_raw_data.sql
```

**Vérification:**
```bash
psql -U postgres -d service_public_db -c "SELECT COUNT(*) FROM raw.communes; SELECT COUNT(*) FROM raw.centres_service;"
```

**Expected:** Voir les compteurs (ex: 202 communes, 57 centres)

---

### ÉTAPE 3: ✅ Transformer les données en DW
```bash
psql -U postgres -d service_public_db -f 04_transform_to_dw.sql
```

**Vérification:**
```bash
psql -U postgres -d service_public_db -c "SELECT COUNT(*) FROM dw.dim_territoire; SELECT COUNT(*) FROM dw.fact_demandes;"
```

**Expected:** Voir les compteurs de territoire et faits

---

### ÉTAPE 4: ✅ Créer les vues analytiques
```bash
psql -U postgres -d service_public_db -f 05_create_views.sql
```

**Vérification:**
```bash
psql -U postgres -d service_public_db -c "\dv dw.*"
```

**Expected:** Voir 7 vues listées

---

### ÉTAPE 5: ✅ Vérifier les KPI globaux
```bash
psql -U postgres -d service_public_db -c "SELECT * FROM dw.v_tableau_bord_principal;"
```

**Expected Output:**
```
total_demandes_globales | territoires_couverts | nombre_centres | ...
--------------------+---------------------+----------------+
      [nombre]       |      [nombre]       |    [nombre]    |
```

---

## 🔍 VÉRIFICATIONS COMPLÈTES

### Vérification 1: Structure générale
```sql
-- Afficher les schémas
\dn

-- Afficher les tables RAW
\dt raw.*

-- Afficher les tables DW
\dt dw.*

-- Afficher les vues
\dv dw.*
```

### Vérification 2: Intégrité des données
```sql
-- Vérifier les doublons
SELECT 'dim_territoire' as table_name, COUNT(*) as total, COUNT(DISTINCT id_territoire) as unique_ids FROM dw.dim_territoire
UNION ALL
SELECT 'fact_demandes', COUNT(*), COUNT(DISTINCT id_fact) FROM dw.fact_demandes;

-- Vérifier les clés étrangères
SELECT * FROM dw.fact_demandes WHERE id_territoire IS NULL;
SELECT * FROM dw.fact_demandes WHERE id_type_document IS NULL;
```

### Vérification 3: Performance
```sql
-- Voir la taille des tables
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname IN ('raw', 'dw')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 📊 TESTS ANALYTIQUES

### Test 1: Top 10 communes
```bash
psql -U postgres -d service_public_db -c "SELECT * FROM dw.v_analyse_geographique LIMIT 10;"
```

### Test 2: Résumé par région
```bash
psql -U postgres -d service_public_db -c "SELECT * FROM dw.v_resume_region;"
```

### Test 3: Requêtes avancées
```bash
psql -U postgres -d service_public_db -f 07_queries_advanced.sql
```

---

## 📝 CHECKLIST POST-INSTALLATION

- [ ] Base de données créée (`service_public_db` existe)
- [ ] Tables RAW remplies (communes, centres, demandes, socio)
- [ ] Dimension TERRITOIRE remplie (tous les niveaux géo)
- [ ] Tables DW remplies (dimensions + faits)
- [ ] Vues créées et accessibles (7 vues)
- [ ] KPI globaux affichables
- [ ] Top 10 communes exécutable
- [ ] Requêtes avancées fonctionnelles
- [ ] Aucune clé étrangère cassée
- [ ] Index présents et optimisants

---

## 🆘 TROUBLESHOOTING

### Problème: "La base n'existe pas"
```bash
# Solution
psql -U postgres -f 00_create_all.sql
```

### Problème: "Tables RAW vides"
```bash
# Vérifier les chemins dans 03_load_raw_data.sql
# Vérifier les fichiers CSV existent
ls -la ../02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/

# Vérifier les permissions
chmod 644 ../02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/*.csv
```

### Problème: "Foreign Key violation"
```bash
# Vérifier dim_territoire est remplie
SELECT COUNT(*) FROM dw.dim_territoire;

# Vérifier que les jointures existent
SELECT COUNT(*) FROM dw.fact_demandes f
LEFT JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
WHERE t.id_territoire IS NULL;
```

### Problème: "Requête lente"
```bash
# Réindexer
REINDEX INDEX idx_fact_demandes_territoire;

# Analyser
VACUUM ANALYZE dw.fact_demandes;
```

---

## 🎓 COMMANDS PostgreSQL UTILES

```bash
# Se connecter à la base
psql -U postgres -d service_public_db

# Exécuter un script
psql -U postgres -d service_public_db -f script.sql

# Exécuter une requête simple
psql -U postgres -d service_public_db -c "SELECT * FROM dw.v_tableau_bord_principal;"

# Export en CSV
psql -U postgres -d service_public_db --csv -c "SELECT * FROM dw.v_resume_region;" > output.csv

# Exécuter avec timing
psql -U postgres -d service_public_db -c "SELECT COUNT(*) FROM dw.fact_demandes;" --timing
```

---

## ✨ PROCHAINES ÉTAPES

1. **Maintenance programmée**
   ```bash
   # Exécuter régulièrement
   psql -U postgres -d service_public_db -f 06_maintenance.sql
   ```

2. **Recharger les données** (si CSV mises à jour)
   ```bash
   psql -U postgres -d service_public_db -f 03_load_raw_data.sql
   psql -U postgres -d service_public_db -f 04_transform_to_dw.sql
   ```

3. **Créer des dashboards**
   - DBeaver pour visualiser les données
   - Jupyter pour les analyses
   - Grafana pour les dashboards

4. **Ajouter des données**
   - Charger de nouveaux CSV
   - Transformer en DW
   - Générer les rapports

---

## 📋 RÉSUMÉ FINAL

| Étape | Status | Commande |
|-------|--------|----------|
| 1. Créer BD | ✓ | `psql -U postgres -f 00_create_all.sql` |
| 2. Charger RAW | ✓ | `psql -U postgres -d service_public_db -f 03_load_raw_data.sql` |
| 3. Transformer DW | ✓ | `psql -U postgres -d service_public_db -f 04_transform_to_dw.sql` |
| 4. Vues | ✓ | `psql -U postgres -d service_public_db -f 05_create_views.sql` |
| 5. Vérifier | ✓ | `psql -U postgres -d service_public_db -c "SELECT * FROM dw.v_tableau_bord_principal;"` |

---

## 🎉 VOUS ÊTES PRÊT!

La base de données est opérationnelle et prête pour l'analyse des services publics au Togo.

**Fichiers documentation:**
- README.md - Vue d'ensemble
- GUIDE_COMPLET.md - Guide détaillé
- CHECKLIST.md - Cette checklist
- 07_queries_advanced.sql - Requêtes d'analyse

---

**Date:** Janvier 2026
**Projet:** Public Services Optimization - Togo
**Statut:** ✅ PRÊT POUR PRODUCTION
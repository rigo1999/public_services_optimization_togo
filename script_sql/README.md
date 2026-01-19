# Scripts SQL - Service Public DB

## Architecture Data Warehouse

Cette base de données suit une architecture professionnelle **3 niveaux** :

```
RAW (CSV bruts) → DW (Dimensions + Faits) → VUE (Analyses)
```

### Schémas
- **`raw`** : Tables de chargement direct des CSV (sans transformation)
- **`dw`** : Modèle analytique dimensionnel (Dimensions + Table de Faits)

### Dimension Centrale
- **`dw.dim_territoire`** : Clé unique pour tous les niveaux géographiques (région, préfecture, commune, quartier)

---

## 📋 Ordre d'exécution

### 🚀 Option 1 : Exécution automatique (recommandée)

```bash
# Exécuter le script d'orchestration (crée tout en une seule commande)
psql -U postgres -f 00_create_all.sql
```

Ce script crée :
- ✅ La base de données
- ✅ Les schémas RAW et DW
- ✅ La dimension TERRITOIRE
- ✅ Toutes les tables RAW
- ✅ Toutes les tables DW

### 🔧 Option 2 : Exécution étape par étape

#### Étape 1 : Création des structures
```bash
psql -U postgres -f 01_create_database.sql
psql -U postgres -d service_public_db -f 02_create_tables.sql
```

#### Étape 2 : Chargement des données RAW
```bash
psql -U postgres -d service_public_db -f 03_load_raw_data.sql
```

#### Étape 3 : Transformation RAW → DW
```bash
psql -U postgres -d service_public_db -f 04_transform_to_dw.sql
```

#### Étape 4 : Création des vues analytiques
```bash
psql -U postgres -d service_public_db -f 05_create_views.sql
```

---

## 📁 Fichiers détail

| Fichier | Description |
|---------|-------------|
| **00_create_all.sql** | 🚀 Orchestration complète (tout en un) |
| **01_create_database.sql** | Crée la base `service_public_db` |
| **02_create_tables.sql** | Crée schémas, dimensions et tables DW |
| **03_load_raw_data.sql** | Charge les CSV dans les tables RAW |
| **04_transform_to_dw.sql** | Transforme RAW → DW (dimensions + faits) |
| **05_create_views.sql** | Crée 7 vues analytiques |

---

## 📊 Architecture détaillée

### Tables RAW (Chargement CSV)
```
raw.communes
raw.centres_service
raw.demandes_services_public
raw.donnees_socioeconomiques
```

### Dimension Centrale
```
dw.dim_territoire (clé: region, prefecture, commune, quartier)
```

### Dimensions Analytiques
```
dw.dim_communes              (référence géographique)
dw.dim_centres_service       (centres de services)
dw.dim_type_document         (types/catégories)
dw.dim_socioeconomique       (démographie)
```

### Table de Faits
```
dw.fact_demandes             (mesures: volume, délai, taux rejet)
```

### Vues Analytiques
```
dw.v_resume_region                  (résumé par région)
dw.v_performance_centres            (performance des centres)
dw.v_indicateurs_socio              (indicateurs socio-économiques)
dw.v_analyse_documents              (analyse par type de document)
dw.v_tendance_temporelle            (tendances temporelles)
dw.v_analyse_geographique           (analyse géographique)
dw.v_tableau_bord_principal         (KPI globaux)
```

---

## 🔌 Connexion à la base

```bash
# Connexion simple
psql -U postgres -d service_public_db

# Avec hôte/port
psql -h localhost -p 5432 -U postgres -d service_public_db
```

---

## ✅ Vérification de l'installation

```sql
-- Voir les schémas
\dn

-- Voir les tables par schéma
\dt raw.*
\dt dw.*

-- Voir les vues
\dv dw.*

-- Vérifier les données chargées
SELECT 'dim_territoire' as table_name, COUNT(*) as row_count FROM dw.dim_territoire
UNION ALL
SELECT 'fact_demandes', COUNT(*) FROM dw.fact_demandes
UNION ALL
SELECT 'dim_centres_service', COUNT(*) FROM dw.dim_centres_service
UNION ALL
SELECT 'dim_socioeconomique', COUNT(*) FROM dw.dim_socioeconomique;

-- Consulter le tableau de bord principal
SELECT * FROM dw.v_tableau_bord_principal;
```

---

## 🔍 Exemples de requêtes

### Demandes par région
```sql
SELECT * FROM dw.v_resume_region;
```

### Performance des centres
```sql
SELECT * FROM dw.v_performance_centres 
WHERE statut_centre = 'Actif'
ORDER BY volume_demandes DESC;
```

### Indicateurs socio-économiques
```sql
SELECT * FROM dw.v_indicateurs_socio;
```

### Analyse des délais par document
```sql
SELECT * FROM dw.v_analyse_documents 
ORDER BY total_demandes DESC;
```

---

## ⚙️ Configuration

| Point | Détail |
|-------|--------|
| **Encodage** | UTF-8 (support français) |
| **Dimension centrale** | `dw.dim_territoire` (clé technique + unicité métier) |
| **Index** | Sur id_territoire, date_demande, type_document |
| **Contraintes** | Unicité sur dim_territoire et dim_type_document |
| **Performance** | Optimisée pour les JOIN sur id_territoire |

---

## 📝 Notes importantes

1. **Permissions** : L'utilisateur PostgreSQL doit pouvoir créer bases de données et schémas
2. **Chemins CSV** : Vérifier les chemins dans `03_load_raw_data.sql`
3. **UTF-8** : Assurez-vous que PostgreSQL utilise UTF-8
4. **Réexécution** : Exécuter `00_create_all.sql` supprimera et recréera la base

---

## 🆘 Aide

Documentation PostgreSQL : https://www.postgresql.org/docs/

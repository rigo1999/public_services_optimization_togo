# 🚀 LANCER LA CRÉATION DE LA BASE DE DONNÉES

## ⚠️ PRÉREQUIS
PostgreSQL doit être installé et en cours d'exécution.

### Vérifier si PostgreSQL est installé:
```powershell
psql --version
```

Si non installé, téléchargez depuis: https://www.postgresql.org/download/windows/

---

## 🎯 OPTION 1: Script Python (RECOMMANDÉ)
```powershell
# Dans le dossier script_sql
python install_postgresql_db.py
```

Avantages:
- ✅ Gère les erreurs gracieusement
- ✅ Fournit des messages clairs
- ✅ Fonctionne avec psycopg2

---

## 🎯 OPTION 2: PowerShell
```powershell
# Dans le dossier script_sql
.\setup_db.ps1
```

Avantages:
- ✅ Interface visuelle claire
- ✅ Spécifique à Windows

---

## 🎯 OPTION 3: Batch (Windows)
```cmd
# Dans le dossier script_sql
run_create_db.bat
```

---

## 🎯 OPTION 4: Ligne de commande directe
```powershell
# Exécution directe du script SQL
psql -U postgres -f 00_create_all.sql
```

---

## ✅ VÉRIFICATION APRÈS CRÉATION

```powershell
# Se connecter à la base
psql -U postgres -d service_public_db

# Dans psql, vérifier les schémas
\dn

# Vérifier les tables
\dt dw.*

# Compter les enregistrements
SELECT COUNT(*) FROM dw.dim_territoire;
```

---

## 📊 STRUCTURE CRÉÉE

```
service_public_db
├── Schema: dw (Data Warehouse)
│   ├── dim_territoire (table centrale)
│   └── (d'autres tables seront créées)
└── Schema: raw (données brutes)
    └── (données importées des CSV)
```

---

## 🔧 DÉPANNAGE

### PostgreSQL n'est pas trouvé
```
Solution: Ajouter PostgreSQL au PATH Windows
- Aller à C:\Program Files\PostgreSQL\<version>\bin
- Copier le chemin
- Ajouter aux variables d'environnement PATH
```

### Erreur de connexion
```
Vérifier:
- PostgreSQL est en cours d'exécution (Services Windows)
- L'utilisateur 'postgres' existe
- Le port 5432 est accessible
- psycopg2 est installé: pip install psycopg2
```

### Mot de passe incorrect
```
Le script utilise par défaut: postgres
Si votre mot de passe est différent, modifiez les scripts
```

---

## 📝 FICHIERS INCLUS

- `00_create_all.sql` - Script principal (tous les éléments)
- `01_create_database.sql` - Création de la base
- `02_create_tables.sql` - Création des tables
- `03_load_raw_data.sql` - Chargement des données brutes
- `04_transform_to_dw.sql` - Transformation vers le Data Warehouse
- `05_create_views.sql` - Vues analytiques
- `install_postgresql_db.py` - Installation complète (Python)
- `setup_db.ps1` - Installation (PowerShell)
- `run_create_db.bat` - Installation (Batch)

---

## 🎓 COMMANDES UTILES APRÈS INSTALLATION

```sql
-- Se connecter
psql -U postgres -d service_public_db

-- Afficher les tables
\dt

-- Afficher les schémas
\dn

-- Afficher les vues
\dv

-- Exporter une table
\COPY table_name TO 'file.csv' WITH (FORMAT csv, HEADER true);

-- Supprimer la base (attention!)
DROP DATABASE service_public_db;
```

---

**Besoin d'aide?** Consultez la documentation PostgreSQL: https://www.postgresql.org/docs/

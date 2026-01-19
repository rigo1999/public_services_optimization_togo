# 📋 GUIDE COMPLET - CRÉATION DE LA BASE DE DONNÉES

## ❌ PROBLÈME ACTUEL
PostgreSQL n'est **pas installé** sur votre système.

---

## ✅ SOLUTIONS (du plus simple au plus complexe)

### 📌 OPTION 1: Docker (Recommandé - Aucune installation)
Le plus rapide si vous avez Docker installé.

**Avantages:**
- ✅ Pas d'installation PostgreSQL directe
- ✅ Isolation complète
- ✅ Facile à désinstaller

**Étapes:**
```powershell
# 1. Installer Docker Desktop (si non fait)
#    https://www.docker.com/products/docker-desktop

# 2. Lancer le conteneur PostgreSQL
python docker_setup.py

# 3. Ensuite créer la base
python install_postgresql_db.py
```

---

### 📌 OPTION 2: Installation Directe PostgreSQL (Plus traditionnel)

**Téléchargement:**
1. Aller sur https://www.postgresql.org/download/windows/
2. Télécharger PostgreSQL 15 ou 16
3. Installer avec les paramètres par défaut
4. Noter le mot de passe pour 'postgres'

**Après installation:**
```powershell
# Vérifier
psql --version

# Créer la base
python install_postgresql_db.py
```

---

### 📌 OPTION 3: Installation via Chocolatey (Pour développeurs)

**Prérequis:** Avoir Chocolatey installé

```powershell
# Lancer PowerShell EN ADMIN
choco install postgresql
```

Puis:
```powershell
python install_postgresql_db.py
```

---

### 📌 OPTION 4: WSL2 + PostgreSQL (Pour utilisateurs avancés)

**Si vous avez WSL2 d'installé:**
```bash
# Dans le terminal WSL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Démarrer le service
sudo service postgresql start

# Créer l'utilisateur postgres
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

Puis depuis PowerShell:
```powershell
python install_postgresql_db.py
```

---

## 🚀 ÉTAPES RAPIDES POUR COMMENCER

### Pour Docker (Plus recommandé):
```powershell
cd script_sql
python docker_setup.py
# Attendre que le conteneur démarre (~30s)
python install_postgresql_db.py
```

### Pour Installation Native:
```powershell
# 1. Installer PostgreSQL depuis https://www.postgresql.org/download/windows/
# 2. Redémarrer
# 3. Puis:
cd script_sql
python install_postgresql_db.py
```

---

## ✅ VÉRIFIER QUE TOUT FONCTIONNE

Après installation, testez la connexion:

```powershell
# Pour PostgreSQL local
psql -U postgres -d service_public_db -c "SELECT 1;"

# Pour Docker
docker exec -it service_public_db psql -U postgres -d service_public_db -c "SELECT 1;"
```

Si vous voyez `1`, c'est bon! ✅

---

## 📊 CE QUI SERA CRÉÉ

Après exécution du script, vous aurez:

```
Database: service_public_db
│
├── Schema: dw (Data Warehouse)
│   ├── dim_territoire (dimension centrale des régions/communes)
│   ├── fact_demandes (faits sur les demandes)
│   ├── dim_centre_service (centres de services)
│   └── dim_temps (dimension temporelle)
│
└── Schema: raw (données brutes)
    ├── centres_service
    ├── demandes_services_public
    ├── communes
    └── donnees_socioeconomiques
```

---

## 🔧 SCRIPTS DISPONIBLES

| Script | Description | Quand l'utiliser |
|--------|-------------|-----------------|
| `install_postgresql_db.py` | Installation complète | Toujours en premier |
| `docker_setup.py` | Setup Docker PostgreSQL | Si Docker installé |
| `setup_db.ps1` | PowerShell setup | Alternative Windows |
| `00_create_all.sql` | Script SQL principal | Exécuté automatiquement |

---

## ❓ FAQ

### Q: Je n'ai pas Docker ni PostgreSQL, quoi faire?
**R:** Installez PostgreSQL depuis https://www.postgresql.org/download/windows/

### Q: Docker est trop complexe?
**R:** Installez PostgreSQL directement, c'est plus simple.

### Q: Le mot de passe par défaut, c'est quoi?
**R:** `postgres` (vous pouvez le changer après)

### Q: Comment accéder à la base?
**R:** `psql -U postgres -d service_public_db`

### Q: Comment charger les données CSV?
**R:** Un script `load_data.py` sera créé après la base

### Q: Je peux utiliser SQLite?
**R:** Oui, mais PostgreSQL est meilleur pour ce cas d'usage

---

## 📞 SUPPORT

Si vous rencontrez des problèmes:

1. **Vérifier les prérequis:**
   ```powershell
   psql --version
   docker --version  # si Docker
   ```

2. **Vérifier PostgreSQL est en cours d'exécution:**
   - Windows: Services → PostgreSQL
   - Docker: `docker ps`

3. **Vérifier le port:**
   ```powershell
   netstat -ano | findstr :5432
   ```

4. **Réinstaller si nécessaire:**
   - Désinstaller PostgreSQL/Docker
   - Redémarrer
   - Réinstaller

---

## 🎯 PROCHAINES ÉTAPES

1. ✅ Installer PostgreSQL ou Docker
2. ✅ Exécuter `python install_postgresql_db.py`
3. ✅ Vérifier la connexion
4. ✅ Charger les données CSV
5. ✅ Créer les requêtes analytiques

Bon courage! 🚀

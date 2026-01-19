@echo off
REM Script d'installation et création de la base de données
REM Vérifie PostgreSQL et crée la base service_public_db

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║    CRÉATION DE LA BASE DE DONNÉES SERVICE PUBLIC DB        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Vérifier si PostgreSQL est installé
echo Recherche de PostgreSQL...
where psql >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ✗ PostgreSQL n'est pas installé ou non accessible dans le PATH
    echo.
    echo OPTIONS:
    echo   1. Installer PostgreSQL depuis: https://www.postgresql.org/download/windows/
    echo   2. Ajouter le chemin PostgreSQL au PATH
    echo   3. Ou utiliser le script Python: python setup_database.py
    echo.
    pause
    exit /b 1
)

echo ✓ PostgreSQL trouvé

REM Créer la base de données
echo.
echo Connexion à PostgreSQL et création de la base...
echo.

REM Exécuter le script SQL principal
psql -U postgres -f 00_create_all.sql

if %errorlevel% equ 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║         ✅ BASE DE DONNÉES CRÉÉE AVEC SUCCÈS!             ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo Prochaines étapes:
    echo   - Vérifier la base: psql -U postgres -d service_public_db
    echo   - Charger les données: python load_data.py
    echo.
) else (
    echo.
    echo ✗ Erreur lors de la création de la base
    echo.
)

pause

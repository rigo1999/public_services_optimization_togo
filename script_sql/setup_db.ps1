# Script PowerShell pour créer la base de données PostgreSQL
# Usage: .\setup_db.ps1

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║    CRÉATION DE LA BASE DE DONNÉES SERVICE PUBLIC DB        ║
║                                                            ║
║ Ce script va créer et initialiser la base PostgreSQL       ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host "`n[ÉTAPE 1] Vérification de PostgreSQL...`n" -ForegroundColor Yellow

# Vérifier si psql est accessible
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if ($null -eq $psqlPath) {
    Write-Host "✗ PostgreSQL n'est pas trouvé dans le PATH`n" -ForegroundColor Red
    Write-Host "Options pour installer PostgreSQL:" -ForegroundColor Yellow
    Write-Host "  1. Télécharger depuis: https://www.postgresql.org/download/windows/" -ForegroundColor Green
    Write-Host "  2. Installer depuis Chocolatey (admin): choco install postgresql" -ForegroundColor Green
    Write-Host "  3. Après installation, ajouter au PATH: C:\Program Files\PostgreSQL\<version>\bin" -ForegroundColor Green
    Write-Host "`nOu utiliser l'alternative Python:" -ForegroundColor Yellow
    Write-Host "  python setup_database.py`n" -ForegroundColor Green
    exit 1
}

Write-Host "✓ PostgreSQL trouvé: $($psqlPath.Source)`n" -ForegroundColor Green

Write-Host "[ÉTAPE 2] Création de la base de données...`n" -ForegroundColor Yellow

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Exécuter le script SQL principal
Write-Host "Exécution de 00_create_all.sql..." -ForegroundColor Cyan
psql -U postgres -f 00_create_all.sql

if ($LASTEXITCODE -eq 0) {
    Write-Host @"
╔════════════════════════════════════════════════════════════╗
║         ✅ BASE DE DONNÉES CRÉÉE AVEC SUCCÈS!             ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

    Write-Host "`nProchaines étapes:`n" -ForegroundColor Yellow
    Write-Host "  1️⃣  Se connecter à la base:" -ForegroundColor Cyan
    Write-Host "     psql -U postgres -d service_public_db`n" -ForegroundColor Green
    
    Write-Host "  2️⃣  Afficher les schémas:" -ForegroundColor Cyan
    Write-Host "     SELECT schema_name FROM information_schema.schemata;`n" -ForegroundColor Green
    
    Write-Host "  3️⃣  Afficher les tables:" -ForegroundColor Cyan
    Write-Host "     \dt dw.*`n" -ForegroundColor Green
    
    Write-Host "  4️⃣  Charger les données CSV:" -ForegroundColor Cyan
    Write-Host "     python load_data.py`n" -ForegroundColor Green
    
    Write-Host "  5️⃣  Vérifier les dimensions:" -ForegroundColor Cyan
    Write-Host "     SELECT COUNT(*) FROM dw.dim_territoire;`n" -ForegroundColor Green
} else {
    Write-Host "`n✗ Erreur lors de la création de la base`n" -ForegroundColor Red
    exit 1
}

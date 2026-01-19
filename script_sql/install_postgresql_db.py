"""
Script complet d'installation et d'initialisation de la base de données PostgreSQL
Usage: python install_postgresql_db.py
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}  {text}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_step(num, text):
    print(f"{Colors.BOLD}{Colors.BLUE}[ÉTAPE {num}]{Colors.END} {text}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def check_postgresql():
    """Vérifie si PostgreSQL est installé"""
    print_step(1, "Vérification de PostgreSQL...")
    
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"PostgreSQL trouvé: {version}")
            return True
    except FileNotFoundError:
        pass
    
    print_error("PostgreSQL n'est pas trouvé dans le PATH")
    return False

def install_postgresql_windows():
    """Offre des options d'installation pour Windows"""
    print_info("PostgreSQL doit être installé sur votre système")
    print(f"\n{Colors.YELLOW}Options d'installation:{Colors.END}")
    print("  1. Télécharger depuis: https://www.postgresql.org/download/windows/")
    print("  2. Ou utiliser Chocolatey (en admin):")
    print(f"     {Colors.BOLD}choco install postgresql{Colors.END}")
    print("  3. Après installation, redémarrez ce script")
    print("\nPendant l'installation:")
    print("  - Acceptez tous les paramètres par défaut")
    print("  - Notez le mot de passe pour l'utilisateur 'postgres'")
    print("  - Port par défaut: 5432")

def create_database_python():
    """Crée la base de données en utilisant Python et psycopg2"""
    print_step(2, "Création de la base de données avec Python...")
    
    try:
        import psycopg2
        print_success("psycopg2 est disponible")
    except ImportError:
        print_error("psycopg2 n'est pas installé")
        print(f"\nInstallez avec: {Colors.BOLD}pip install psycopg2{Colors.END}\n")
        return False
    
    try:
        # Connexion au serveur PostgreSQL
        print_info("Connexion à PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres"
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Supprimer la base existante
        try:
            print_info("Suppression de la base existante...")
            cursor.execute("DROP DATABASE IF EXISTS service_public_db;")
            print_success("Base existante supprimée")
        except:
            pass
        
        # Créer la nouvelle base
        print_info("Création de la nouvelle base...")
        cursor.execute("CREATE DATABASE service_public_db ENCODING 'UTF8';")
        print_success("Base de données créée: service_public_db")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print_error(f"Impossible de se connecter à PostgreSQL: {str(e)[:100]}")
        print_info("Vérifiez que PostgreSQL est en cours d'exécution")
        print_info("Port par défaut: localhost:5432")
        print_info("Utilisateur par défaut: postgres")
        return False

def create_database_psql():
    """Crée la base de données en utilisant psql"""
    print_step(2, "Création de la base de données avec psql...")
    
    script_dir = Path(__file__).parent
    
    try:
        result = subprocess.run(
            ['psql', '-U', 'postgres', '-f', str(script_dir / '00_create_all.sql')],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Base de données créée avec succès")
            return True
        else:
            print_error(f"Erreur: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {str(e)[:100]}")
        return False

def main():
    os_name = platform.system()
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print_header("INSTALLATION - BASE DE DONNÉES SERVICE PUBLIC DB")
    
    print(f"Système d'exploitation: {os_name}")
    print(f"Répertoire: {script_dir}\n")
    
    # Vérifier PostgreSQL
    postgres_installed = check_postgresql()
    
    if not postgres_installed:
        print()
        if os_name == "Windows":
            install_postgresql_windows()
        else:
            print_error("PostgreSQL doit être installé: sudo apt-get install postgresql")
        return False
    
    # Créer la base de données
    print()
    try:
        success = create_database_psql()
    except:
        print_info("Tentative avec Python...")
        success = create_database_python()
    
    if success:
        print_header("✅ INSTALLATION RÉUSSIE")
        print(f"{Colors.GREEN}La base de données 'service_public_db' est prête!{Colors.END}\n")
        
        print(f"{Colors.BOLD}Prochaines étapes:{Colors.END}")
        print(f"  1. Se connecter: {Colors.BOLD}psql -U postgres -d service_public_db{Colors.END}")
        print(f"  2. Charger les données: {Colors.BOLD}python load_data.py{Colors.END}")
        print(f"  3. Vérifier: {Colors.BOLD}SELECT COUNT(*) FROM dw.dim_territoire;{Colors.END}\n")
        return True
    else:
        print_header("✗ INSTALLATION ÉCHOUÉE")
        print(f"{Colors.RED}Veuillez vérifier l'installation de PostgreSQL{Colors.END}\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

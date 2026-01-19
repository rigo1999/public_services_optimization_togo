"""
Alternative: Créer un conteneur Docker avec PostgreSQL
Usage: python docker_setup.py
"""

import subprocess
import sys
import json

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{text:^60}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def check_docker():
    """Vérifie si Docker est installé"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Docker trouvé: {result.stdout.strip()}{Colors.END}")
            return True
    except:
        pass
    
    print(f"{Colors.RED}✗ Docker n'est pas trouvé{Colors.END}")
    return False

def setup_docker_postgresql():
    """Configure PostgreSQL dans un conteneur Docker"""
    print_header("LANCER POSTGRESQL DANS DOCKER")
    
    if not check_docker():
        print(f"\n{Colors.YELLOW}Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop{Colors.END}\n")
        return False
    
    print(f"\n{Colors.CYAN}Étape 1: Téléchargement de l'image PostgreSQL...{Colors.END}")
    try:
        subprocess.run(['docker', 'pull', 'postgres:latest'], 
                      capture_output=True)
        print(f"{Colors.GREEN}✓ Image téléchargée{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ Erreur: {e}{Colors.END}")
        return False
    
    print(f"\n{Colors.CYAN}Étape 2: Création du conteneur...{Colors.END}")
    try:
        subprocess.run([
            'docker', 'run',
            '-d',
            '--name', 'service_public_db',
            '-e', 'POSTGRES_PASSWORD=postgres',
            '-e', 'POSTGRES_DB=service_public_db',
            '-p', '5432:5432',
            '-v', 'postgres_data:/var/lib/postgresql/data',
            'postgres:latest'
        ], capture_output=True)
        print(f"{Colors.GREEN}✓ Conteneur créé et lancé{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ Erreur: {e}{Colors.END}")
        return False
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✅ PostgreSQL est maintenant accessible!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Connexion:{Colors.END}")
    print(f"  Hôte: localhost")
    print(f"  Port: 5432")
    print(f"  Utilisateur: postgres")
    print(f"  Mot de passe: postgres")
    print(f"  Base: service_public_db\n")
    
    print(f"{Colors.BOLD}Commandes utiles:{Colors.END}")
    print(f"  docker exec -it service_public_db psql -U postgres -d service_public_db")
    print(f"  docker stop service_public_db")
    print(f"  docker start service_public_db")
    print(f"  docker remove service_public_db\n")
    
    return True

if __name__ == "__main__":
    print_header("SETUP POSTGRESQL AVEC DOCKER")
    
    success = setup_docker_postgresql()
    
    if success:
        print(f"\n{Colors.YELLOW}Maintenant, exécutez:{Colors.END}")
        print(f"  python install_postgresql_db.py\n")
    
    sys.exit(0 if success else 1)

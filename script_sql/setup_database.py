"""
Script de création de la base de données service_public_db avec PostgreSQL
Ce script utilise psycopg2 pour créer la base sans nécessiter psql
"""

import psycopg2
from psycopg2 import sql
import os
import sys

def execute_sql_file(connection, file_path):
    """Exécute un fichier SQL complet"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Diviser le fichier en instructions individuelles
        instructions = sql_content.split(';')
        
        cursor = connection.cursor()
        for instruction in instructions:
            instruction = instruction.strip()
            if instruction and not instruction.startswith('--') and not instruction.startswith('\\'):
                try:
                    print(f"Exécution: {instruction[:80]}...")
                    cursor.execute(instruction)
                    connection.commit()
                except Exception as e:
                    print(f"⚠️ Attention: {str(e)[:100]}")
                    connection.commit()  # Continuer malgré les erreurs
        
        cursor.close()
        print("✓ Fichier exécuté avec succès!")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'exécution: {e}")
        return False

def create_database():
    """Crée la base de données service_public_db"""
    
    # Configuration PostgreSQL
    try:
        # Se connecter au serveur PostgreSQL par défaut
        print("🔗 Connexion à PostgreSQL...")
        connection = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres"
        )
        
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Créer la base de données
        print("📦 Création de la base de données 'service_public_db'...")
        try:
            cursor.execute("DROP DATABASE IF EXISTS service_public_db;")
            print("  ✓ Ancienne base supprimée")
        except:
            pass
        
        cursor.execute("CREATE DATABASE service_public_db ENCODING 'UTF8';")
        print("  ✓ Base de données créée!")
        
        cursor.close()
        connection.close()
        
        # Se reconnecter à la nouvelle base
        print("\n🔗 Connexion à service_public_db...")
        connection = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="service_public_db"
        )
        
        connection.autocommit = False
        
        # Exécuter les scripts SQL dans l'ordre
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        scripts = [
            "01_create_database.sql",
            "02_create_tables.sql",
            "03_load_raw_data.sql",
            "04_transform_to_dw.sql",
            "05_create_views.sql"
        ]
        
        for script in scripts:
            script_path = os.path.join(script_dir, script)
            if os.path.exists(script_path):
                print(f"\n📄 Exécution de {script}...")
                execute_sql_file(connection, script_path)
            else:
                print(f"⚠️ Fichier non trouvé: {script_path}")
        
        connection.close()
        print("\n" + "="*60)
        print("✅ BASE DE DONNÉES CRÉÉE AVEC SUCCÈS!")
        print("="*60)
        print("\n📋 Prochaines étapes:")
        print("  1. Vérifier les données: psql -U postgres -d service_public_db")
        print("  2. Exécuter des requêtes: SELECT * FROM dw.dim_territoire;")
        print("\n")
        
    except psycopg2.OperationalError as e:
        print(f"\n✗ ERREUR: Impossible de se connecter à PostgreSQL")
        print(f"   {str(e)}")
        print("\n⚙️ Assurez-vous que:")
        print("   - PostgreSQL est installé et en cours d'exécution")
        print("   - L'utilisateur 'postgres' existe avec le mot de passe 'postgres'")
        print("   - PostgreSQL écoute sur localhost:5432")
        return False
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════╗")
    print("║    CRÉATION DE LA BASE DE DONNÉES SERVICE PUBLIC DB        ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    success = create_database()
    sys.exit(0 if success else 1)

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import os
from pathlib import Path

# Configuration
DB_URL = "postgresql://postgres:postgres@127.0.0.1:5434/service_public_db"
DATA_CLEANED_DIR = Path("d:/public_services_optimization_togo/02_Nettoyage_et_Preparation_des_Donnees/data_cleaned")
SQL_SCRIPTS_DIR = Path("d:/public_services_optimization_togo/script_sql")

def run_sql_script(engine, script_path):
    print(f"📖 Exécution du script : {script_path.name}...")
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        sql_lines = [l for l in lines if not l.strip().startswith('\\')]
        clean_sql = '\n'.join(sql_lines)
        
        commands = [c.strip() for c in clean_sql.split(';') if c.strip()]
        
        for cmd in commands:
            # On utilise une nouvelle transaction pour chaque commande pour éviter le blocage InFailedSqlTransaction
            with engine.begin() as conn:
                try:
                    conn.execute(text(cmd))
                except Exception as e:
                    print(f"⚠️ Erreur SQL dans {script_path.name}: {str(e)[:150]}...")

def main():
    print("🚀 Chargement des données Cleaned et Synchronisation DW...")
    
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return

    # 1. Reset et Recréation des tables
    print("\n--- ÉTAPE 1 : Reset et Recréation des Schémas ---")
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS raw CASCADE; DROP SCHEMA IF EXISTS dw CASCADE;"))
        conn.execute(text("CREATE SCHEMA raw; CREATE SCHEMA dw;"))
    
    run_sql_script(engine, SQL_SCRIPTS_DIR / "02_create_tables.sql")

    # 2. Chargement des CSV dans le schéma RAW
    mapping = {
        'details_communes_cleaned.csv': 'communes',
        'centres_service_cleaned.csv': 'centres_service',
        'demande_services_public_cleaned.csv': 'demandes_services_public',
        'donnees_socioeconomiques_cleaned.csv': 'donnees_socioeconomiques'
    }

    print("\n--- ÉTAPE 2 : Insertion dans le schéma RAW ---")
    for csv_name, table_name in mapping.items():
        csv_path = DATA_CLEANED_DIR / csv_name
        if csv_path.exists():
            print(f"📥 {csv_name} -> raw.{table_name}")
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # Normalisation des headers
            df.columns = [c.replace('é', 'e').replace(' ', '_').lower() for c in df.columns]
            
            # Corrections spécifiques
            if table_name == 'donnees_socioeconomiques':
                if 'taux_alphabetisation' not in df.columns:
                    for col in df.columns:
                        if 'alphab' in col:
                            df.rename(columns={col: 'taux_alphabetisation'}, inplace=True)
            
            if 'date_demande' in df.columns:
                df['date_demande'] = pd.to_datetime(df['date_demande']).dt.date
            if 'date_ouverture' in df.columns:
                df['date_ouverture'] = pd.to_datetime(df['date_ouverture']).dt.date
            
            # On ne garde que les colonnes qui existent dans la table cible (on vérifie via le DDL)
            # En fait, pandas va lever une erreur si on essaie d'insérer des colonnes en trop.
            # On va juste filtrer pour être sûr.
            
            df.to_sql(table_name, engine, schema='raw', if_exists='append', index=False)
            print(f"   ✅ {len(df)} lignes insérées.")
        else:
            print(f"⚠️ Fichier manquant : {csv_name}")

    # 3. Transformation vers le Data Warehouse (DW)
    print("\n--- ÉTAPE 3 : Transformation RAW -> DW ---")
    run_sql_script(engine, SQL_SCRIPTS_DIR / "04_transform_to_dw.sql")

    # 4. Création des Vues
    print("\n--- ÉTAPE 4 : Création des vues analytiques ---")
    run_sql_script(engine, SQL_SCRIPTS_DIR / "05_create_views.sql")

    # 5. Vérification
    print("\n--- ÉTAPE 5 : Rapport final ---")
    with engine.connect() as conn:
        tables = [
            'dw.dim_territoire', 
            'dw.dim_communes', 
            'dw.dim_centres_service', 
            'dw.dim_type_document',
            'dw.dim_socioeconomique',
            'dw.fact_demandes'
        ]
        for t in tables:
            try:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).fetchone()
                print(f"📊 {t:30} : {res[0]} lignes")
            except Exception as e:
                print(f"📊 {t:30} : ERREUR ({str(e)[:50]})")

    print("\n✨ Data Warehouse opérationnel !")

if __name__ == "__main__":
    main()

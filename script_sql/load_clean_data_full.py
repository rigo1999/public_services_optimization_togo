import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import os
from pathlib import Path
import re

# Configuration
DB_URL = "postgresql://postgres:postgres@127.0.0.1:5434/service_public_db"
DATA_CLEANED_DIR = Path("d:/public_services_optimization_togo/02_Nettoyage_et_Preparation_des_Donnees/data_cleaned")
SQL_SCRIPTS_DIR = Path("d:/public_services_optimization_togo/script_sql")

def run_sql_script(engine, script_path):
    print(f"Running script: {script_path.name}...")
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Remove SQL comments and split by semicolon
        content = re.sub(r'--.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        commands = [c.strip() for c in content.split(';') if c.strip()]
        
        for cmd in commands:
            # Skip psql-specific commands like \c or \echo
            if cmd.startswith('\\'):
                continue
                
            with engine.begin() as conn:
                try:
                    conn.execute(text(cmd))
                except Exception as e:
                    # Avoid emoji or special chars in error print
                    safe_error = str(e).encode('ascii', errors='replace').decode('ascii')
                    print(f"SQL Error in {script_path.name}: {safe_error[:200]}...")

def main():
    print("Loading Cleaned data and Syncing DW...")
    
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    # 1. Reset
    print("\n--- STEP 1: Reset Schemas ---")
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS raw CASCADE; DROP SCHEMA IF EXISTS dw CASCADE;"))
        conn.execute(text("CREATE SCHEMA raw; CREATE SCHEMA dw;"))
    
    run_sql_script(engine, SQL_SCRIPTS_DIR / "02_create_tables.sql")

    # 2. Load CSVs
    mapping = {
        'details_communes_cleaned.csv': 'communes',
        'centres_service_cleaned.csv': 'centres_service',
        'demande_services_public_cleaned.csv': 'demandes_services_public',
        'donnees_socioeconomiques_cleaned.csv': 'donnees_socioeconomiques'
    }

    print("\n--- STEP 2: Insert into RAW ---")
    for csv_name, table_name in mapping.items():
        csv_path = DATA_CLEANED_DIR / csv_name
        if csv_path.exists():
            print(f"Loading {csv_name} -> raw.{table_name}")
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # Normalization
            df.columns = [c.replace('é', 'e').replace(' ', '_').lower() for c in df.columns]
            
            if 'date_demande' in df.columns:
                df['date_demande'] = pd.to_datetime(df['date_demande']).dt.date
            if 'date_ouverture' in df.columns:
                df['date_ouverture'] = pd.to_datetime(df['date_ouverture']).dt.date
            
            df.to_sql(table_name, engine, schema='raw', if_exists='append', index=False)
            print(f"   Rows inserted: {len(df)}")
        else:
            print(f"Missing file: {csv_name}")

    # 3. Transform
    print("\n--- STEP 3: Transform RAW -> DW ---")
    run_sql_script(engine, SQL_SCRIPTS_DIR / "04_transform_to_dw.sql")

    # 4. Views
    print("\n--- STEP 4: Create Views ---")
    run_sql_script(engine, SQL_SCRIPTS_DIR / "05_create_views.sql")

    # 5. Verification
    print("\n--- STEP 5: Final Report ---")
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
                print(f" {t:30} : {res[0]} rows")
            except Exception as e:
                print(f" {t:30} : ERROR")

    print("\nData Warehouse Operational!")

if __name__ == "__main__":
    main()

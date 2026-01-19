"""
Script de chargement des données nettoyées dans PostgreSQL
Charge les dimensions et faits depuis les fichiers CSV nettoyés
"""

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import os
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
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}  {text}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_step(num, text):
    print(f"{Colors.BOLD}{Colors.BLUE}[ÉTAPE {num}]{Colors.END} {text}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def get_db_engine():
    """Crée une connexion à la base de données PostgreSQL"""
    print_step(1, "Connexion à PostgreSQL...")
    
    try:
        # Configuration Docker
        engine = create_engine(
            'postgresql://postgres:postgres@127.0.0.1:5434/service_public_db',
            echo=False
        )
        
        # Test de connexion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print_success(f"Connecté à PostgreSQL")
            print_info(f"Version: {version[:50]}...")
        
        return engine
    
    except Exception as e:
        print_error(f"Impossible de se connecter: {str(e)}")
        return None

def load_cleaned_data():
    """Charge les fichiers CSV nettoyés"""
    print_step(2, "Chargement des fichiers CSV nettoyés...")
    
    data_dir = Path(__file__).parent.parent / "02_Nettoyage_et_Preparation_des_Donnees" / "data_cleaned"
    
    data = {}
    files_to_load = {
        'centres': 'centres_service_cleaned.csv',
        'demandes': 'demande_services_public_cleaned.csv',
        'documents': 'document_administratif_cleaned.csv',
        'socioeco': 'donnees_socioeconomiques_cleaned.csv',
        'communes': 'details_communes_cleaned.csv',
        'developpement': 'developpement_cleaned.csv',
    }
    
    for key, filename in files_to_load.items():
        filepath = data_dir / filename
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                data[key] = df
                print_success(f"Chargé: {filename} ({len(df)} lignes)")
            except Exception as e:
                print_error(f"Erreur chargement {filename}: {str(e)[:100]}")
        else:
            print_info(f"Fichier non trouvé: {filename}")
    
    return data

def load_dim_territoire(engine, data):
    """Charge la dimension TERRITOIRE"""
    print_step(3, "Chargement de DIM_TERRITOIRE...")
    
    try:
        # D'abord, supprimer toutes les tables dépendantes
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS dw.dim_demande CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS dw.dim_document CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS dw.dim_socioeconomique CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS dw.dim_commune CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS dw.dim_developpement CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS dw.dim_reseau CASCADE;"))
            conn.commit()
        
        # Colonnes de territoire présentes dans chaque dataset
        territoire_cols = ["region", "prefecture", "commune"]
        
        dfs_to_concat = []
        
        # Centres de services
        if 'centres' in data:
            cols = [c for c in territoire_cols if c in data['centres'].columns]
            if cols:
                dfs_to_concat.append(data['centres'][cols])
                print_info(f"Centres: {len(data['centres'])} lignes")
        
        # Demandes
        if 'demandes' in data:
            cols = [c for c in territoire_cols if c in data['demandes'].columns]
            if cols:
                dfs_to_concat.append(data['demandes'][cols])
                print_info(f"Demandes: {len(data['demandes'])} lignes")
        
        # Documents
        if 'documents' in data:
            cols = [c for c in territoire_cols if c in data['documents'].columns]
            if cols:
                dfs_to_concat.append(data['documents'][cols])
                print_info(f"Documents: {len(data['documents'])} lignes")
        
        # Données socioéconomiques
        if 'socioeco' in data:
            cols = [c for c in territoire_cols if c in data['socioeco'].columns]
            if cols:
                dfs_to_concat.append(data['socioeco'][cols])
                print_info(f"Socioéconomiques: {len(data['socioeco'])} lignes")
        
        if not dfs_to_concat:
            print_error("Aucune colonne de territoire trouvée")
            return False
        
        # Concaténer et dédupliquer
        df_territoire = pd.concat(dfs_to_concat, ignore_index=True).drop_duplicates()
        
        print_info(f"Total lignes avant déduplication: {sum(len(df) for df in dfs_to_concat)}")
        print_info(f"Total lignes après déduplication: {len(df_territoire)}")
        
        # Ajouter ID
        df_territoire.insert(0, 'territoire_id', range(1, len(df_territoire) + 1))
        
        # Charger dans la base
        df_territoire.to_sql(
            "dim_territoire",
            engine,
            schema="dw",
            if_exists="replace",
            index=False
        )
        
        print_success(f"DIM_TERRITOIRE chargée: {len(df_territoire)} territoires uniques")
        return True
    
    except Exception as e:
        print_error(f"Erreur chargement DIM_TERRITOIRE: {str(e)}")
        return False
        
        dfs_to_concat = []
        
        # Centres de services
        if 'centres' in data:
            cols = [c for c in territoire_cols if c in data['centres'].columns]
            if cols:
                dfs_to_concat.append(data['centres'][cols])
                print_info(f"Centres: {len(data['centres'])} lignes")
        
        # Demandes
        if 'demandes' in data:
            cols = [c for c in territoire_cols if c in data['demandes'].columns]
            if cols:
                dfs_to_concat.append(data['demandes'][cols])
                print_info(f"Demandes: {len(data['demandes'])} lignes")
        
        # Documents
        if 'documents' in data:
            cols = [c for c in territoire_cols if c in data['documents'].columns]
            if cols:
                dfs_to_concat.append(data['documents'][cols])
                print_info(f"Documents: {len(data['documents'])} lignes")
        
        # Données socioéconomiques
        if 'socioeco' in data:
            cols = [c for c in territoire_cols if c in data['socioeco'].columns]
            if cols:
                dfs_to_concat.append(data['socioeco'][cols])
                print_info(f"Socioéconomiques: {len(data['socioeco'])} lignes")
        
        if not dfs_to_concat:
            print_error("Aucune colonne de territoire trouvée")
            return False
        
        # Concaténer et dédupliquer
        df_territoire = pd.concat(dfs_to_concat, ignore_index=True).drop_duplicates()
        
        print_info(f"Total lignes avant déduplication: {sum(len(df) for df in dfs_to_concat)}")
        print_info(f"Total lignes après déduplication: {len(df_territoire)}")
        
        # Ajouter ID
        df_territoire.insert(0, 'territoire_id', range(1, len(df_territoire) + 1))
        
        # Charger dans la base - utiliser append pour préserver les FKs
        df_territoire.to_sql(
            "dim_territoire",
            engine,
            schema="dw",
            if_exists="replace",
            index=False
        )
        
        print_success(f"DIM_TERRITOIRE chargée: {len(df_territoire)} territoires uniques")
        return True
    
    except Exception as e:
        print_error(f"Erreur chargement DIM_TERRITOIRE: {str(e)}")
        return False

def load_dim_centre(engine, data):
    """Charge la dimension CENTRE avec tous les attributs"""
    print_step(4, "Chargement de DIM_CENTRE...")
    
    try:
        if 'centres' not in data:
            print_error("Données de centres non trouvées")
            return False
        
        df_centres = data['centres'].copy()
        
        # Créer un mapping région+préfecture+commune -> territoire_id
        with engine.connect() as conn:
            query = text("""
                SELECT territoire_id, region, prefecture, commune 
                FROM dw.dim_territoire
            """)
            territoire_data = conn.execute(query).fetchall()
            
            # Créer un dictionnaire de lookup
            territoire_map = {}
            for tid, region, prefecture, commune in territoire_data:
                key = (region, prefecture, commune)
                territoire_map[key] = tid
        
        # Mapper les centres aux territoires
        def get_territoire_id(row):
            key = (row.get('region'), row.get('prefecture'), row.get('commune'))
            return territoire_map.get(key)
        
        df_centres['id_territoire'] = df_centres.apply(get_territoire_id, axis=1)
        
        # Filtrer les centres avec territoire_id valide
        df_centres_valid = df_centres[df_centres['id_territoire'].notna()].copy()
        
        print_info(f"Centres avec territoire: {len(df_centres_valid)}/{len(df_centres)}")
        
        # Préparer les colonnes pour le chargement
        df_centres_prep = pd.DataFrame({
            'centre_id': df_centres_valid.get('centre_id', ''),
            'nom_centre': df_centres_valid.get('nom_centre', ''),
            'type_centre': df_centres_valid.get('type_centre', ''),
            'region': df_centres_valid.get('region', ''),
            'prefecture': df_centres_valid.get('prefecture', ''),
            'commune': df_centres_valid.get('commune', ''),
            'quartier': df_centres_valid.get('quartier', ''),
            'latitude': df_centres_valid.get('latitude', None),
            'longitude': df_centres_valid.get('longitude', None),
            'personnel_capacite_jour': df_centres_valid.get('personnel_capacite_jour', 0),
            'nombre_guichets': df_centres_valid.get('nombre_guichets', 0),
            'heures_ouverture': df_centres_valid.get('heures_ouverture', ''),
            'horaire_nuit': df_centres_valid.get('horaire_nuit', ''),
            'equipement_numerique': df_centres_valid.get('equipement_numerique', ''),
            'date_ouverture': df_centres_valid.get('date_ouverture', None),
            'statut_centre': df_centres_valid.get('statut_centre', ''),
            'annee_ouverture': df_centres_valid.get('annee_ouverture', 0),
            'mois_ouverture': df_centres_valid.get('mois_ouverture', 0),
            'id_territoire': df_centres_valid['id_territoire']
        })
        
        # Charger dans la base
        df_centres_prep.to_sql(
            "dim_centre",
            engine,
            schema="dw",
            if_exists="replace",
            index=False
        )
        
        print_success(f"DIM_CENTRE chargée: {len(df_centres_prep)} centres avec tous les attributs")
        return True
    
    except Exception as e:
        print_error(f"Erreur chargement DIM_CENTRE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def load_fact_demandes(engine, data):
    """Charge la table de faits FACT_DEMANDES"""
    print_step(5, "Chargement de FACT_DEMANDES...")
    
    try:
        if 'demandes' not in data:
            print_error("Données de demandes non trouvées")
            return False
        
        df_demandes = data['demandes'].copy()
        
        # Charger dans la base
        df_demandes.to_sql(
            "fact_demandes",
            engine,
            schema="dw",
            if_exists="replace",
            index=False
        )
        
        print_success(f"FACT_DEMANDES chargée: {len(df_demandes)} demandes")
        return True
    
    except Exception as e:
        print_error(f"Erreur chargement FACT_DEMANDES: {str(e)}")
        return False

def load_dim_demande(engine, data):
    """Charge DIM_DEMANDE avec FK à territoire"""
    print_step(5, "Chargement de DIM_DEMANDE...")
    try:
        if 'demandes' not in data:
            return False
        df = data['demandes'].copy()
        
        # Mapper territoires
        with engine.connect() as conn:
            territoire_data = conn.execute(text("SELECT territoire_id, region, prefecture, commune FROM dw.dim_territoire")).fetchall()
            territoire_map = {(t[1], t[2], t[3]): t[0] for t in territoire_data}
        
        df['id_territoire'] = df.apply(lambda r: territoire_map.get((r.get('region'), r.get('prefecture'), r.get('commune'))), axis=1)
        df_valid = df[df['id_territoire'].notna()]
        
        df_valid.to_sql("dim_demande", engine, schema="dw", if_exists="replace", index=False)
        print_success(f"DIM_DEMANDE chargée: {len(df_valid)} demandes")
        return True
    except Exception as e:
        print_error(f"Erreur DIM_DEMANDE: {str(e)}")
        return False

def load_dim_document(engine, data):
    """Charge DIM_DOCUMENT avec FK à territoire"""
    print_step(6, "Chargement de DIM_DOCUMENT...")
    try:
        if 'documents' not in data:
            return False
        df = data['documents'].copy()
        
        # Mapper territoires
        with engine.connect() as conn:
            territoire_data = conn.execute(text("SELECT territoire_id, region, prefecture, commune FROM dw.dim_territoire")).fetchall()
            territoire_map = {(t[1], t[2], t[3]): t[0] for t in territoire_data}
        
        df['id_territoire'] = df.apply(lambda r: territoire_map.get((r.get('region'), r.get('prefecture'), r.get('commune'))), axis=1)
        df_valid = df[df['id_territoire'].notna()]
        
        df_valid.to_sql("dim_document", engine, schema="dw", if_exists="replace", index=False)
        print_success(f"DIM_DOCUMENT chargée: {len(df_valid)} documents")
        return True
    except Exception as e:
        print_error(f"Erreur DIM_DOCUMENT: {str(e)}")
        return False

def load_dim_socioeconomique(engine, data):
    """Charge DIM_SOCIOECONOMIQUE avec FK à territoire"""
    print_step(7, "Chargement de DIM_SOCIOECONOMIQUE...")
    try:
        if 'socioeco' not in data:
            return False
        df = data['socioeco'].copy()
        
        # Mapper territoires
        with engine.connect() as conn:
            territoire_data = conn.execute(text("SELECT territoire_id, region, prefecture, commune FROM dw.dim_territoire")).fetchall()
            territoire_map = {(t[1], t[2], t[3]): t[0] for t in territoire_data}
        
        df['id_territoire'] = df.apply(lambda r: territoire_map.get((r.get('region'), r.get('prefecture'), r.get('commune'))), axis=1)
        df_valid = df[df['id_territoire'].notna()]
        
        df_valid.to_sql("dim_socioeconomique", engine, schema="dw", if_exists="replace", index=False)
        print_success(f"DIM_SOCIOECONOMIQUE chargée: {len(df_valid)} territoires")
        return True
    except Exception as e:
        print_error(f"Erreur DIM_SOCIOECONOMIQUE: {str(e)}")
        return False

def verify_loaded_data(engine):
    """Vérifie les données chargées"""
    print_step(5, "Vérification des données chargées...")
    
    try:
        with engine.connect() as conn:
            # Vérifier les tables
            query = text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'dw' 
                ORDER BY tablename
            """)
            tables = conn.execute(query).fetchall()
            
            print_info(f"Tables dans le schéma dw:")
            for (table,) in tables:
                count_query = text(f"SELECT COUNT(*) FROM dw.{table}")
                count = conn.execute(count_query).fetchone()[0]
                print(f"  • {table}: {count:,} lignes")
        
        return True
    
    except Exception as e:
        print_error(f"Erreur vérification: {str(e)}")
        return False

def main():
    print_header("CHARGEMENT DES DONNÉES VERS POSTGRESQL")
    
    # Connexion à la base
    engine = get_db_engine()
    if not engine:
        return False
    
    # Charger les données
    data = load_cleaned_data()
    if not data:
        print_error("Aucune donnée chargée")
        return False
    
    # Charger les dimensions et faits
    success = True
    success = success and load_dim_territoire(engine, data)
    success = success and load_dim_centre(engine, data)
    success = success and load_dim_demande(engine, data)
    success = success and load_dim_document(engine, data)
    success = success and load_dim_socioeconomique(engine, data)
    success = success and load_fact_demandes(engine, data)
    
    # Vérifier
    if success:
        verify_loaded_data(engine)
        
        print_header("✅ CHARGEMENT RÉUSSI")
        print(f"{Colors.GREEN}Les données sont maintenant dans PostgreSQL!{Colors.END}\n")
        
        print(f"{Colors.BOLD}Prochaines étapes:{Colors.END}")
        print(f"  1. Explorer dans pgAdmin4")
        print(f"  2. Écrire des requêtes d'analyse")
        print(f"  3. Créer des visualisations\n")
    else:
        print_header("✗ ERREURS LORS DU CHARGEMENT")
        return False
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

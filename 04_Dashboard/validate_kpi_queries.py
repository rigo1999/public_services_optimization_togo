"""
Script de Validation des Requêtes KPI
====================================

Teste la connectivité à PostgreSQL et valide que tous les KPI
peuvent être exécutés correctement.

Usage: python validate_kpi_queries.py
"""

import sys
import psycopg2
import psycopg2.extras
from datetime import datetime
import traceback

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'service_public_db'
}

# Définition des KPI queries
KPI_QUERIES = {
    'KPI-001-Global': """
        SELECT 
            ROUND(AVG(delai_traitement_jours)::NUMERIC, 2) as delai_moyen_jours,
            COUNT(*) as nombre_demandes
        FROM dw.fact_demandes fd
        WHERE delai_traitement_jours IS NOT NULL;
    """,
    
    'KPI-002-Global': """
        SELECT 
            COUNT(CASE WHEN statut_demande IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::INTEGER as demandes_traitees,
            COUNT(*)::INTEGER as total_demandes,
            ROUND((COUNT(CASE WHEN statut_demande IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::NUMERIC 
                   / NULLIF(COUNT(*), 0)) * 100, 2) as taux_absorption_pct
        FROM dw.fact_demandes;
    """,
    
    'KPI-003': """
        SELECT 
            region,
            COUNT(DISTINCT prefecture)::INTEGER as prefectures_total,
            COUNT(DISTINCT CASE WHEN prefecture IS NOT NULL THEN prefecture END)::INTEGER as prefectures_actives,
            ROUND((COUNT(DISTINCT CASE WHEN prefecture IS NOT NULL THEN prefecture END)::NUMERIC 
                   / NULLIF(COUNT(DISTINCT prefecture), 0)) * 100, 2) as taux_couverture_pct
        FROM dw.fact_demandes
        GROUP BY region;
    """,
    
    'KPI-004': """
        SELECT 
            region,
            COUNT(*)::INTEGER as nombre_demandes,
            COUNT(DISTINCT prefecture)::INTEGER as nombre_prefectures,
            ROUND(COUNT(*)::NUMERIC / NULLIF(COUNT(DISTINCT prefecture), 0), 2) as demandes_par_prefecture
        FROM dw.fact_demandes
        GROUP BY region;
    """,
    
    'KPI-005-Global': """
        SELECT 
            COUNT(CASE WHEN statut_demande = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees,
            COUNT(CASE WHEN statut_demande = 'Validée' THEN 1 END)::INTEGER as demandes_validees,
            ROUND((COUNT(CASE WHEN statut_demande = 'Rejetée' THEN 1 END)::NUMERIC 
                   / NULLIF(COUNT(CASE WHEN statut_demande IN ('Rejetée', 'Validée') THEN 1 END), 0)) * 100, 2) as taux_rejet_global_pct
        FROM dw.fact_demandes;
    """,
    
    'KPI-006': """
        SELECT 
            region,
            prefecture,
            COUNT(*)::INTEGER as nombre_demandes,
            ROUND(AVG(nombre_demandes)::NUMERIC, 2) as demandes_moyennes,
            ROUND(AVG(delai_traitement_jours)::NUMERIC, 2) as delai_moyen_jours
        FROM dw.fact_demandes
        GROUP BY region, prefecture;
    """,
    
    'KPI-007': """
        SELECT 
            COALESCE(type_document, 'Non spécifié') as type_document,
            COUNT(*)::INTEGER as nombre_demandes,
            ROUND(AVG(delai_traitement_jours)::NUMERIC, 2) as delai_moyen_jours,
            ROUND(AVG(taux_rejet)::NUMERIC, 2) as taux_rejet_moyen_pct,
            COUNT(CASE WHEN statut_demande = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees
        FROM dw.fact_demandes
        WHERE type_document IS NOT NULL
        GROUP BY type_document;
    """,
    
    'KPI-008': """
        SELECT 
            region,
            prefecture,
            COUNT(CASE WHEN statut_demande IN ('En Attente', 'En Cours') THEN 1 END)::INTEGER as demandes_en_attente,
            COUNT(*)::INTEGER as total_demandes,
            ROUND((COUNT(CASE WHEN statut_demande IN ('En Attente', 'En Cours') THEN 1 END)::NUMERIC 
                   / NULLIF(COUNT(*), 0)) * 100, 2) as taux_saturation_pct
        FROM dw.fact_demandes
        GROUP BY region, prefecture;
    """
}

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def test_connection():
    """Test PostgreSQL connection"""
    print_header("ÉTAPE 1: Test de Connexion PostgreSQL")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Connecté à PostgreSQL")
        print(f"  Version: {version.split(',')[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Erreur de connexion: {str(e)}")
        return False

def check_database_objects():
    """Check if all required tables and schemas exist"""
    print_header("ÉTAPE 2: Vérification des Objets Base de Données")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check schemas
        cursor.execute("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name IN ('dw', 'raw');
        """)
        schemas = [row[0] for row in cursor.fetchall()]
        
        if 'dw' in schemas:
            print("✓ Schéma 'dw' (data warehouse) trouvé")
        else:
            print("✗ Schéma 'dw' manquant")
            return False
        
        # Check tables
        required_tables = [
            'dim_centre', 'dim_territoire', 'dim_demande', 'dim_document',
            'dim_socioeconomique', 'fact_demandes'
        ]
        
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'dw';
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n  Tables trouvées dans schéma 'dw':")
        for table in tables:
            print(f"  ✓ {table}")
        
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"\n  ✗ Tables manquantes: {', '.join(missing)}")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {str(e)}")
        return False

def validate_kpi_queries():
    """Validate all KPI queries"""
    print_header("ÉTAPE 3: Validation des Requêtes KPI")
    
    results = {}
    conn = None
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        
        for kpi_name, query in KPI_QUERIES.items():
            try:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cursor.execute(query)
                rows = cursor.fetchall()
                row_count = len(rows)
                
                print(f"\n✓ {kpi_name}")
                print(f"  Résultats: {row_count} ligne(s)")
                
                if row_count > 0 and row_count <= 3:
                    for i, row in enumerate(rows[:3], 1):
                        print(f"    Ligne {i}: {dict(row)}")
                elif row_count > 3:
                    print(f"    Affichage des 3 premiers résultats:")
                    for i, row in enumerate(rows[:3], 1):
                        # Truncate long values
                        row_dict = {k: (str(v)[:40] + '...' if isinstance(v, str) and len(str(v)) > 40 else v) 
                                   for k, v in dict(row).items()}
                        print(f"    Ligne {i}: {row_dict}")
                
                results[kpi_name] = {'status': 'OK', 'rows': row_count}
                cursor.close()
                
            except Exception as e:
                print(f"\n✗ {kpi_name}")
                print(f"  Erreur: {str(e)}")
                results[kpi_name] = {'status': 'ERREUR', 'message': str(e)}
    
    except Exception as e:
        print(f"✗ Erreur de connexion lors de la validation KPI: {str(e)}")
        return False
    
    finally:
        if conn:
            conn.close()
    
    return all(r['status'] == 'OK' for r in results.values())

def get_table_row_counts():
    """Get row counts for all dimension and fact tables"""
    print_header("ÉTAPE 4: Statistiques des Tables")
    
    tables = {
        'dw.dim_centre': 'Centres de Service',
        'dw.dim_territoire': 'Territoires',
        'dw.dim_demande': 'Demandes',
        'dw.dim_document': 'Types de Document',
        'dw.dim_socioeconomique': 'Données Socioéconomiques',
        'dw.fact_demandes': 'Faits Demandes'
    }
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for table_name, description in tables.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"✓ {description:30} ({table_name:25}): {count:>6} lignes")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {str(e)}")
        return False

def main():
    """Main validation function"""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  VALIDATION DES REQUÊTES KPI - TABLEAU DE BORD STREAMLIT".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    print(f"\nDate/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    all_ok = True
    
    # Run all tests
    if not test_connection():
        print("\n✗ ARRÊT: Impossible de se connecter à PostgreSQL")
        return False
    
    if not check_database_objects():
        print("\n✗ ARRÊT: Objets base de données manquants")
        return False
    
    if not get_table_row_counts():
        print("\n⚠ Avertissement: Impossible de compter les lignes des tables")
        all_ok = False
    
    if not validate_kpi_queries():
        print("\n✗ ERREUR: Certaines requêtes KPI ont échoué")
        all_ok = False
    
    # Summary
    print_header("RÉSUMÉ FINAL")
    if all_ok:
        print("✅ TOUS LES TESTS PASSED - Le tableau de bord est prêt!")
        print("\nPour lancer le dashboard:")
        print("  Windows: run_dashboard.bat")
        print("  Linux/Mac: streamlit run app_streamlit.py")
        return True
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ - Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

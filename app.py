"""
🚀 Streamlit Dashboard - Service Public DB
Dashboard pour visualiser et analyser la base de données PostgreSQL service_public_db
"""

import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Service Public Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("📊 Service Public Database Dashboard")
st.markdown("---")

# Configuration de la connexion PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'service_public_db',
    'user': 'postgres',
    'password': 'postgres'
}

@st.cache_resource
def get_connection():
    """Créer une connexion à PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"❌ Erreur de connexion: {str(e)}")
        st.info("💡 Assurez-vous que PostgreSQL Docker est en cours d'exécution")
        return None

@st.cache_data
def load_data(query):
    """Charger les données depuis PostgreSQL"""
    try:
        conn = get_connection()
        if conn:
            df = pd.read_sql(query, conn)
            return df
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None

# Sidebar - Navigation
with st.sidebar:
    st.title("🎯 Navigation")
    page = st.radio("Sélectionnez une page:", 
                    ["📈 Accueil", "🏢 Centres Service", "📋 Demandes", 
                     "👥 Données Socio-éco", "🗺️ Territoires", "⚙️ Connexion"])

# PAGE 1: Accueil
if page == "📈 Accueil":
    st.header("Bienvenue! 👋")
    st.markdown("""
    ### À propos de ce Dashboard
    
    Ce dashboard vous permet de visualiser et analyser les données de:
    - **Centres de services publics**
    - **Demandes de services**
    - **Données socio-économiques**
    - **Territoires (régions, communes)**
    
    ### 📊 Fonctionnalités
    - 📈 Graphiques interactifs
    - 📋 Tableaux de données
    - 🔍 Filtres personnalisés
    - 💾 Export de données
    
    ### 🚀 Pour commencer
    Sélectionnez une section dans le menu latéral.
    """)
    
    # Statistiques rapides
    st.markdown("---")
    st.subheader("📌 Statistiques Rapides")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            
            # Nombre de centres
            cursor.execute("SELECT COUNT(*) FROM centres_service")
            nb_centres = cursor.fetchone()[0]
            col1.metric("🏢 Centres", nb_centres)
            
            # Nombre de demandes
            cursor.execute("SELECT COUNT(*) FROM demandes_services_public")
            nb_demandes = cursor.fetchone()[0]
            col2.metric("📋 Demandes", nb_demandes)
            
            # Communes
            cursor.execute("SELECT COUNT(*) FROM communes")
            nb_communes = cursor.fetchone()[0]
            col3.metric("🏘️ Communes", nb_communes)
            
            # Régions
            cursor.execute("SELECT COUNT(DISTINCT region) FROM communes")
            nb_regions = cursor.fetchone()[0]
            col4.metric("🗺️ Régions", nb_regions)
            
            conn.close()
    except Exception as e:
        st.warning(f"⚠️ Impossible de charger les statistiques: {e}")

# PAGE 2: Centres de Service
elif page == "🏢 Centres Service":
    st.header("🏢 Centres de Services Publics")
    
    try:
        # Charger les données
        df_centres = load_data("SELECT * FROM centres_service LIMIT 100")
        
        if df_centres is not None and len(df_centres) > 0:
            st.subheader(f"📊 Total: {len(df_centres)} centres")
            
            # Onglets
            tab1, tab2, tab3 = st.tabs(["Tableau", "Statistiques", "Carte"])
            
            with tab1:
                st.dataframe(df_centres, use_container_width=True)
            
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Centres par Région")
                    try:
                        query = "SELECT region, COUNT(*) as count FROM centres_service GROUP BY region"
                        df_region = load_data(query)
                        if df_region is not None:
                            fig = px.bar(df_region, x='region', y='count', title="Répartition par Région")
                            st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.warning("Impossible de charger le graphique")
                
                with col2:
                    st.subheader("Statut des Centres")
                    try:
                        query = "SELECT statut_centre, COUNT(*) as count FROM centres_service GROUP BY statut_centre"
                        df_status = load_data(query)
                        if df_status is not None:
                            fig = px.pie(df_status, values='count', names='statut_centre', title="Statut")
                            st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.warning("Impossible de charger le graphique")
            
            with tab3:
                st.info("🗺️ Carte géographique (en développement)")
        else:
            st.warning("❌ Aucune donnée disponible. Assurez-vous que la base est créée.")
    except Exception as e:
        st.error(f"Erreur: {e}")

# PAGE 3: Demandes
elif page == "📋 Demandes":
    st.header("📋 Demandes de Services")
    
    try:
        df_demandes = load_data("SELECT * FROM demandes_services_public LIMIT 100")
        
        if df_demandes is not None and len(df_demandes) > 0:
            st.subheader(f"📊 Total: {len(df_demandes)} demandes")
            st.dataframe(df_demandes, use_container_width=True)
        else:
            st.warning("❌ Aucune donnée disponible.")
    except Exception as e:
        st.error(f"Erreur: {e}")

# PAGE 4: Données Socio-éco
elif page == "👥 Données Socio-éco":
    st.header("👥 Données Socio-économiques")
    
    try:
        df_socio = load_data("SELECT * FROM donnees_socioeconomiques LIMIT 100")
        
        if df_socio is not None and len(df_socio) > 0:
            st.subheader(f"📊 Total: {len(df_socio)} enregistrements")
            st.dataframe(df_socio, use_container_width=True)
        else:
            st.warning("❌ Aucune donnée disponible.")
    except Exception as e:
        st.error(f"Erreur: {e}")

# PAGE 5: Territoires
elif page == "🗺️ Territoires":
    st.header("🗺️ Territoires (Régions & Communes)")
    
    try:
        df_communes = load_data("SELECT * FROM communes LIMIT 100")
        
        if df_communes is not None and len(df_communes) > 0:
            st.subheader(f"📊 Total: {len(df_communes)} communes")
            st.dataframe(df_communes, use_container_width=True)
        else:
            st.warning("❌ Aucune donnée disponible.")
    except Exception as e:
        st.error(f"Erreur: {e}")

# PAGE 6: Connexion
elif page == "⚙️ Connexion":
    st.header("⚙️ Configuration de Connexion")
    
    st.subheader("📡 Paramètres PostgreSQL:")
    st.code(f"""
Host:     {DB_CONFIG['host']}
Port:     {DB_CONFIG['port']}
Database: {DB_CONFIG['database']}
User:     {DB_CONFIG['user']}
    """)
    
    if st.button("🔍 Tester la connexion"):
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                st.success("✅ Connexion réussie!")
                st.info(f"PostgreSQL: {version[:50]}...")
                conn.close()
            else:
                st.error("❌ Connexion échouée")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
    
    st.markdown("---")
    st.subheader("💡 Aide")
    st.markdown("""
    ### Assurez-vous que:
    1. ✅ PostgreSQL Docker est en cours d'exécution
    2. ✅ La base `service_public_db` a été créée
    3. ✅ Les tables ont été créées et les données chargées
    
    ### Commandes utiles:
    ```bash
    # Démarrer Docker PostgreSQL
    docker start service_public_db_togo
    
    # Créer la base
    cd script_sql
    python install_postgresql_db.py
    
    # Lancer ce dashboard
    streamlit run app.py
    ```
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
📊 Service Public Optimization Dashboard | January 2026
</div>
""", unsafe_allow_html=True)

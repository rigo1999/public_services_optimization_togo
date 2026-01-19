"""
Streamlit Dashboard - Optimisation des Services Publics au Togo
===============================================================

Application interactive pour le pilotage des KPI basée sur PostgreSQL
et les données réelles du datawarehouse.

Auteur: Data Warehouse Togo
Date: 2026-01-19
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Tableau de Bord - Services Publics Togo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONNEXION À LA BASE DE DONNÉES
# ============================================================================

@st.cache_resource
def get_db_connection():
    """Établit une connexion PostgreSQL persistante"""
    return psycopg2.connect(
        host="localhost",
        port=5434,
        user="postgres",
        password="postgres",
        dbname="service_public_db"
    )

@st.cache_data(ttl=3600)
def execute_query(query):
    """Exécute une requête SQL et retourne les résultats en DataFrame"""
    try:
        conn = get_db_connection()
        # On ne ferme pas la connexion ici car elle est gérée par @st.cache_resource
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Erreur SQL: {str(e)}")
        return pd.DataFrame()

# ============================================================================
# REQUÊTES KPI
# ============================================================================

def get_kpi_001_dmt_global():
    """KPI-001: Délai Moyen de Traitement (Global)"""
    query = """
    SELECT 
        ROUND(AVG(delai_traitement_jours)::NUMERIC, 2) as delai_moyen_jours,
        COUNT(*) as nombre_demandes
    FROM dw.fact_demandes WHERE delai_traitement_jours IS NOT NULL;
    """
    return execute_query(query)

def get_kpi_001_dmt_par_region():
    """KPI-001: Délai par Région"""
    query = """
    SELECT t.region, ROUND(AVG(f.delai_traitement_jours)::NUMERIC, 2) as delai_moyen_jours,
        COUNT(*) as nombre_demandes
    FROM dw.fact_demandes f
    JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
    WHERE f.delai_traitement_jours IS NOT NULL
    GROUP BY t.region ORDER BY delai_moyen_jours DESC;
    """
    return execute_query(query)

def get_kpi_002_absorption_global():
    """KPI-002: Taux d'Absorption (Global)"""
    query = """
    SELECT 
        COUNT(CASE WHEN statut_demande IN ('Traitee', 'Rejetée', 'Finalisée') THEN 1 END)::INTEGER as demandes_traitees,
        COUNT(*)::INTEGER as total_demandes,
        ROUND((COUNT(CASE WHEN statut_demande IN ('Traitee', 'Rejetée', 'Finalisée') THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 2) as taux_absorption_pct
    FROM dw.fact_demandes;
    """
    return execute_query(query)

def get_kpi_002_absorption_par_region():
    """KPI-002: Absorption par Région"""
    query = """
    SELECT t.region,
        COUNT(CASE WHEN f.statut_demande IN ('Traitee', 'Rejetée', 'Finalisée') THEN 1 END)::INTEGER as demandes_traitees,
        COUNT(*)::INTEGER as total_demandes,
        ROUND((COUNT(CASE WHEN f.statut_demande IN ('Traitee', 'Rejetée', 'Finalisée') THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 2) as taux_absorption_pct
    FROM dw.fact_demandes f
    JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
    GROUP BY t.region ORDER BY taux_absorption_pct ASC;
    """
    return execute_query(query)

def get_kpi_003_couverture():
    """KPI-003: Taux de Couverture Territoriale"""
    query = """
    SELECT 
        t.region,
        COUNT(DISTINCT t.prefecture)::INTEGER as prefectures_total,
        COUNT(DISTINCT CASE WHEN fd.prefecture IS NOT NULL THEN fd.prefecture END)::INTEGER as prefectures_actives,
        ROUND((COUNT(DISTINCT CASE WHEN fd.prefecture IS NOT NULL THEN fd.prefecture END)::NUMERIC / NULLIF(COUNT(DISTINCT t.prefecture), 0)) * 100, 2) as taux_couverture_pct
    FROM dw.dim_territoire t
    LEFT JOIN dw.fact_demandes fd ON t.region = fd.region AND t.prefecture = fd.prefecture
    GROUP BY t.region ORDER BY taux_couverture_pct DESC;
    """
    return execute_query(query)

def get_kpi_004_equite():
    """KPI-004: Ratio Équité d'Accès (Demandes pour 1000 hab)"""
    query = """
    SELECT 
        t.region, 
        COUNT(f.id_fact)::INTEGER as nombre_demandes,
        AVG(s.population)::FLOAT as population_moyenne,
        ROUND(COUNT(f.id_fact)::NUMERIC / NULLIF(AVG(s.population), 0) * 1000, 2) as demandes_pour_1000_hab
    FROM dw.dim_territoire t
    LEFT JOIN dw.fact_demandes f ON t.id_territoire = f.id_territoire
    LEFT JOIN dw.dim_socioeconomique s ON t.id_territoire = s.id_territoire
    WHERE s.population IS NOT NULL
    GROUP BY t.region ORDER BY demandes_pour_1000_hab DESC;
    """
    return execute_query(query)

def get_kpi_005_rejet_global():
    """KPI-005: Taux de Rejet (Global)"""
    query = """
    SELECT 
        COUNT(CASE WHEN statut_demande = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees,
        COUNT(CASE WHEN statut_demande = 'Traitee' THEN 1 END)::INTEGER as demandes_traitees,
        ROUND((COUNT(CASE WHEN statut_demande = 'Rejetée' THEN 1 END)::NUMERIC / NULLIF(COUNT(CASE WHEN statut_demande IN ('Rejetée', 'Traitee') THEN 1 END), 0)) * 100, 2) as taux_rejet_global_pct
    FROM dw.fact_demandes;
    """
    return execute_query(query)

def get_kpi_005_rejet_par_type():
    """KPI-005: Taux de Rejet (Par Type de Document)"""
    query = """
    SELECT COALESCE(td.type_document, 'Non spécifié') as type_document,
        COUNT(CASE WHEN f.statut_demande = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees,
        COUNT(CASE WHEN f.statut_demande = 'Traitee' THEN 1 END)::INTEGER as demandes_traitees,
        ROUND((COUNT(CASE WHEN f.statut_demande = 'Rejetée' THEN 1 END)::NUMERIC / NULLIF(COUNT(CASE WHEN f.statut_demande IN ('Rejetée', 'Traitee') THEN 1 END), 0)) * 100, 2) as taux_rejet_pct
    FROM dw.fact_demandes f
    JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
    WHERE f.statut_demande IN ('Rejetée', 'Traitee')
    GROUP BY td.type_document ORDER BY taux_rejet_pct DESC;
    """
    return execute_query(query)

def get_kpi_006_charge_par_region():
    """KPI-006: Charge de Travail par Région"""
    query = """
    SELECT t.region, COUNT(f.id_fact)::INTEGER as nombre_demandes,
        COUNT(DISTINCT t.prefecture)::INTEGER as prefectures,
        ROUND(COUNT(f.id_fact)::NUMERIC / NULLIF(COUNT(DISTINCT t.prefecture), 0), 2) as charge_par_prefecture
    FROM dw.dim_territoire t
    LEFT JOIN dw.fact_demandes f ON t.id_territoire = f.id_territoire
    GROUP BY t.region ORDER BY charge_par_prefecture DESC;
    """
    return execute_query(query)

def get_kpi_007_perf_type_document():
    """KPI-007: Performance par Type de Document"""
    query = """
    SELECT td.type_document,
        COUNT(f.id_fact)::INTEGER as nombre_demandes,
        ROUND(AVG(f.delai_traitement_jours)::NUMERIC, 2) as delai_moyen_jours,
        ROUND(AVG(f.taux_rejet)::NUMERIC, 2) as taux_rejet_moyen_pct
    FROM dw.fact_demandes f
    JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
    GROUP BY td.type_document ORDER BY delai_moyen_jours DESC;
    """
    return execute_query(query)

def get_kpi_centres_capacite_demande():
    """Capacité vs Demande par Centre (Agrégé au niveau Commune)"""
    query = """
    WITH demande_commune AS (
        SELECT t.region, t.prefecture, t.commune,
               SUM(f.nombre_demandes) as total_demandes,
               COUNT(DISTINCT f.date_demande) as nb_jours
        FROM dw.fact_demandes f
        JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
        GROUP BY t.region, t.prefecture, t.commune
    ),
    centres_commune AS (
        SELECT t.region, t.prefecture, t.commune,
               COUNT(*) as nb_centres
        FROM dw.dim_centres_service cs
        JOIN dw.dim_territoire t ON cs.id_territoire = t.id_territoire
        GROUP BY t.region, t.prefecture, t.commune
    )
    SELECT 
        cs.nom_centre,
        t.region,
        cs.personnel_capacite_jour as capacite_quotidienne,
        COALESCE(ROUND((dc.total_demandes::NUMERIC / NULLIF(dc.nb_jours, 0)) / NULLIF(cc.nb_centres, 0), 2), 0) as demande_quotidienne_estimee
    FROM dw.dim_centres_service cs
    JOIN dw.dim_territoire t ON cs.id_territoire = t.id_territoire
    LEFT JOIN demande_commune dc ON t.region = dc.region 
                                AND t.prefecture = dc.prefecture 
                                AND t.commune = dc.commune
    LEFT JOIN centres_commune cc ON t.region = cc.region 
                                AND t.prefecture = cc.prefecture 
                                AND t.commune = cc.commune
    WHERE cs.nom_centre IS NOT NULL
    ORDER BY demande_quotidienne_estimee DESC;
    """
    return execute_query(query)

def get_centres_carto():
    """Récupère les coordonnées des centres pour la carte"""
    query = """
    SELECT 
        cs.nom_centre, 
        cs.type_centre,
        t.region,
        t.prefecture,
        t.commune,
        t.latitude::FLOAT as lat, 
        t.longitude::FLOAT as lon
    FROM dw.dim_centres_service cs
    JOIN dw.dim_territoire t ON cs.id_territoire = t.id_territoire
    WHERE t.latitude IS NOT NULL AND t.longitude IS NOT NULL;
    """
    return execute_query(query)

def get_kpi_008_saturation_region():
    """KPI-008: Saturation par Région"""
    query = """
    SELECT t.region, COUNT(f.id_fact)::INTEGER as total_demandes,
        COUNT(DISTINCT t.prefecture)::INTEGER as prefectures,
        COUNT(CASE WHEN f.statut_demande = 'En Cours' THEN 1 END)::INTEGER as demandes_en_attente,
        ROUND((COUNT(CASE WHEN f.statut_demande = 'En Cours' THEN 1 END)::NUMERIC / NULLIF(COUNT(f.id_fact), 0)) * 100, 2) as taux_saturation_pct
    FROM dw.dim_territoire t
    LEFT JOIN dw.fact_demandes f ON t.id_territoire = f.id_territoire
    GROUP BY t.region ORDER BY taux_saturation_pct DESC;
    """
    return execute_query(query)

def get_regions():
    """Récupère la liste des régions"""
    query = "SELECT DISTINCT region FROM dw.dim_territoire WHERE region IS NOT NULL ORDER BY region;"
    df = execute_query(query)
    return df['region'].tolist() if not df.empty else []

def get_prefectures_by_region(region):
    """Récupère les préfectures d'une région"""
    query = f"SELECT DISTINCT prefecture FROM dw.dim_territoire WHERE region = '{region}' AND prefecture IS NOT NULL ORDER BY prefecture;"
    df = execute_query(query)
    return df['prefecture'].tolist() if not df.empty else []

# ============================================================================
# UTILITAIRES D'AFFICHAGE
# ============================================================================

def get_status_badge(value, metric_type):
    """Retourne le badge de statut"""
    if metric_type == "DMT":
        if value < 3: return "🟢 Excellent"
        elif value < 5: return "🟢 Bon"
        elif value < 10: return "🟡 Acceptable"
        else: return "🔴 Critique"
    elif metric_type == "Absorption":
        if value > 90: return "🟢 Excellent"
        elif value > 85: return "🟢 Bon"
        elif value > 75: return "🟡 Acceptable"
        else: return "🔴 Critique"
    elif metric_type == "Couverture":
        if value == 100: return "🟢 Complète"
        elif value >= 90: return "🟢 Très Bon"
        elif value >= 80: return "🟡 Bon"
        else: return "🔴 Critique"
    elif metric_type == "Rejet":
        if value < 5: return "🟢 Excellent"
        elif value < 10: return "🟢 Bon"
        elif value < 15: return "🟡 Moyen"
        else: return "🔴 Critique"
    return "⚪ N/A"

# ============================================================================
# PAGES
# ============================================================================

def page_accueil():
    """Page d'accueil"""
    st.title("📊 Tableau de Bord - Services Publics Togo")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    kpi_001 = get_kpi_001_dmt_global()
    kpi_002 = get_kpi_002_absorption_global()
    kpi_005 = get_kpi_005_rejet_global()
    
    with col1:
        if not kpi_001.empty:
            dmt = kpi_001['delai_moyen_jours'].values[0]
            st.metric("DMT (jours)", f"{dmt:.1f}", delta=get_status_badge(dmt, "DMT"))
    
    with col2:
        if not kpi_002.empty:
            absorption = kpi_002['taux_absorption_pct'].values[0]
            st.metric("Absorption (%)", f"{absorption:.1f}%", delta=get_status_badge(absorption, "Absorption"))
    
    with col3:
        if not kpi_005.empty:
            rejet = kpi_005['taux_rejet_global_pct'].values[0]
            st.metric("Rejet (%)", f"{rejet:.1f}%", delta=get_status_badge(rejet, "Rejet"))
    
    with col4:
        if not kpi_002.empty:
            total = kpi_002['total_demandes'].values[0]
            st.metric("Total Demandes", f"{total:,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Délai Moyen par Région")
        df = get_kpi_001_dmt_par_region()
        if not df.empty:
            fig = px.bar(df, x='region', y='delai_moyen_jours', color='delai_moyen_jours',
                        color_continuous_scale="RdYlGn_r", title="DMT par Région")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Taux de Rejet par Type")
        df = get_kpi_005_rejet_par_type()
        if not df.empty:
            fig = px.bar(df.head(10), x='type_document', y='taux_rejet_pct',
                        color='taux_rejet_pct', color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)

def page_executive():
    """Vue Executive"""
    st.title("📈 Vue Executive - Synthèse")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        region = st.selectbox("Région", ["Toutes"] + get_regions())
    with col2:
        if region != "Toutes":
            prefecture = st.selectbox("Préfecture", ["Toutes"] + get_prefectures_by_region(region))
    
    st.markdown("---")
    
    # KPI Synthétiques
    col1, col2, col3, col4 = st.columns(4)
    
    kpi_001 = get_kpi_001_dmt_global()
    with col1:
        if not kpi_001.empty:
            st.metric("KPI-001: DMT", f"{kpi_001['delai_moyen_jours'].values[0]:.1f} j")
    
    kpi_002 = get_kpi_002_absorption_global()
    with col2:
        if not kpi_002.empty:
            st.metric("KPI-002: Absorption", f"{kpi_002['taux_absorption_pct'].values[0]:.1f}%")
    
    kpi_005 = get_kpi_005_rejet_global()
    with col3:
        if not kpi_005.empty:
            st.metric("KPI-005: Rejet", f"{kpi_005['taux_rejet_global_pct'].values[0]:.1f}%")
    
    kpi_003 = get_kpi_003_couverture()
    with col4:
        if not kpi_003.empty:
            couv = kpi_003['taux_couverture_pct'].mean()
            st.metric("KPI-003: Couverture", f"{couv:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Absorption par Région")
        df = get_kpi_002_absorption_par_region()
        if not df.empty:
            fig = px.bar(df, x='region', y='taux_absorption_pct', color='taux_absorption_pct',
                        color_continuous_scale="Greens")
            fig.add_hline(y=85, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Couverture Territoriale")
        df = get_kpi_003_couverture()
        if not df.empty:
            fig = px.bar(df, x='region', y='taux_couverture_pct', color='taux_couverture_pct',
                        color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)

def page_operationnelle():
    """Vue Opérationnelle"""
    st.title("🔧 Vue Opérationnelle")
    st.markdown("---")
    
    metric = st.selectbox("Métrique", ["Délai par Région", "Absorption par Région", "Saturation", "Charge", "Capacité des Centres"])
    
    st.markdown("---")
    
    if metric == "Délai par Région":
        st.subheader("Délai Moyen de Traitement")
        df = get_kpi_001_dmt_par_region()
        if not df.empty:
            fig = px.bar(df, x='region', y='delai_moyen_jours', text='nombre_demandes',
                        color='delai_moyen_jours', color_continuous_scale="RdYlGn_r")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
    
    elif metric == "Absorption par Région":
        st.subheader("Taux d'Absorption")
        df = get_kpi_002_absorption_par_region()
        if not df.empty:
            fig = px.bar(df, x='region', y='taux_absorption_pct', text='total_demandes',
                        color='taux_absorption_pct', color_continuous_scale="Greens")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
    
    elif metric == "Saturation":
        st.subheader("Saturation par Région")
        df = get_kpi_008_saturation_region()
        if not df.empty:
            fig = px.bar(df, x='region', y='taux_saturation_pct',
                        color='taux_saturation_pct', color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
    
    elif metric == "Charge":
        st.subheader("Charge par Région")
        df = get_kpi_006_charge_par_region()
        if not df.empty:
            fig = px.bar(df, x='region', y='charge_par_prefecture',
                        color='charge_par_prefecture', color_continuous_scale="Oranges")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

    elif metric == "Capacité des Centres":
        st.subheader("Analyse Capacité vs Demande Quotidienne")
        st.info("Comparaison entre la capacité théorique (agents) et la demande moyenne réelle observée par jour.")
        df = get_kpi_centres_capacite_demande()
        if not df.empty:
            # Création d'un graphique comparatif (Grouped Bar Chart)
            fig = px.bar(df.head(20), x='nom_centre', y=['capacite_quotidienne', 'demande_quotidienne_estimee'],
                        barmode='group', title="Top 20 Centres : Capacité vs Demande (Quotidien)",
                        labels={'value': 'Nombre de Personnes/Demandes', 'variable': 'Indicateur'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Alerte sur les centres en sur-capacité (Demande > Capacité)
            surplus = df[df['demande_quotidienne_estimee'] > df['capacite_quotidienne']]
            if not surplus.empty:
                st.warning(f"⚠️ {len(surplus)} centres sont potentiellement en surcharge (Demande > Capacité).")
            
            st.dataframe(df)

def page_territoriale():
    """Vue Territoriale"""
    st.title("🗺️ Vue Territoriale")
    st.markdown("---")
    
    metric = st.selectbox("Analyse", ["Couverture", "Équité", "Performance Document", "Rejet"])
    
    st.markdown("---")
    
    if metric == "Couverture":
        st.subheader("Analyse de la Couverture Territoriale")
        
        # Carte des centres
        df_carto = get_centres_carto()
        if not df_carto.empty:
            st.markdown("### 🗺️ Carte des Centres de Service")
            fig_map = px.scatter_mapbox(df_carto, lat="lat", lon="lon", 
                                       hover_name="nom_centre", 
                                       hover_data=["region", "prefecture", "type_centre"],
                                       color="type_centre",
                                       zoom=6, height=500)
            fig_map.update_layout(mapbox_style="carto-positron")
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
            st.markdown("---")

        st.subheader("Taux de Couverture par Région")
        df = get_kpi_003_couverture()
        if not df.empty:
            fig = px.bar(df, x='region', y='taux_couverture_pct',
                        color='taux_couverture_pct', color_continuous_scale="Blues")
            fig.add_hline(y=90, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
    
    elif metric == "Équité":
        st.subheader("Équité d'Accès - Demandes/Préfecture")
        df = get_kpi_004_equite()
        if not df.empty:
            fig = px.bar(df, x='region', y='demandes_par_prefecture',
                        color='demandes_par_prefecture', color_continuous_scale="Oranges")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
    
    elif metric == "Performance Document":
        st.subheader("Performance par Type de Document")
        df = get_kpi_007_perf_type_document()
        if not df.empty:
            fig = px.bar(df, x='type_document', y='delai_moyen_jours', color='taux_rejet_moyen_pct',
                        color_continuous_scale="RdYlGn_r")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
    
    elif metric == "Rejet":
        st.subheader("Taux de Rejet par Type de Document")
        df = get_kpi_005_rejet_par_type()
        if not df.empty:
            fig = px.bar(df.head(15), x='type_document', y='taux_rejet_pct',
                        color='taux_rejet_pct', color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Fonction principale"""
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio("Sélectionnez une vue:",
        ["📊 Accueil", "📈 Executive", "🔧 Opérationnelle", "🗺️ Territoriale"])
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Actualisation: {datetime.now().strftime('%H:%M:%S')}")
    
    if page == "📊 Accueil":
        page_accueil()
    elif page == "📈 Executive":
        page_executive()
    elif page == "🔧 Opérationnelle":
        page_operationnelle()
    elif page == "🗺️ Territoriale":
        page_territoriale()

if __name__ == "__main__":
    main()

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
    page_icon="TG",
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
# REQUÊTES KPI (Alignées sur KPI_Definition.md)
# ============================================================================

def get_kpi_001_dmt_global(region=None, prefecture=None, type_doc=None):
    """KPI-001: Délai Moyen de Traitement (DMT)"""
    where_clause = "WHERE f.delai_traitement_jours IS NOT NULL"
    if region and region != "Toutes":
        where_clause += f" AND t.region = '{region}'"
    if prefecture and prefecture != "Toutes":
        where_clause += f" AND t.prefecture = '{prefecture}'"
    if type_doc and type_doc != "Tous":
        where_clause += f" AND td.type_document = '{type_doc}'"
    
    query = f"""
    SELECT 
        ROUND(AVG(f.delai_traitement_jours)::NUMERIC, 2) as delai_moyen_jours,
        COUNT(*) as nombre_demandes
    FROM dw.fact_demandes f
    JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
    JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
    {where_clause};
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

def get_kpi_002_absorption_global(region=None, prefecture=None):
    """KPI-002: Taux d'Absorption (Spec: Validée, Rejetée / Total)"""
    where_clause = "WHERE 1=1"
    if region and region != "Toutes":
        where_clause += f" AND t.region = '{region}'"
    if prefecture and prefecture != "Toutes":
        where_clause += f" AND t.prefecture = '{prefecture}'"

    query = f"""
    SELECT 
        COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END)::INTEGER as demandes_traitees,
        COUNT(*)::INTEGER as total_demandes,
        ROUND((COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 2) as taux_absorption_pct
    FROM dw.fact_demandes f
    JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
    {where_clause};
    """
    return execute_query(query)

def get_kpi_002_absorption_par_region():
    """KPI-002: Absorption par Région"""
    query = """
    SELECT t.region,
        COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END)::INTEGER as demandes_traitees,
        COUNT(*)::INTEGER as total_demandes,
        ROUND((COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 2) as taux_absorption_pct
    FROM dw.fact_demandes f
    JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
    GROUP BY t.region ORDER BY taux_absorption_pct ASC;
    """
    return execute_query(query)

def get_kpi_003_couverture():
    """KPI-003: Taux de Couverture Territoriale (Communes avec Centres / Communes Totales)"""
    query = """
    WITH communes_totales AS (
        SELECT region, COUNT(DISTINCT commune) as total_communes
        FROM dw.dim_territoire
        GROUP BY region
    ),
    communes_avec_centre AS (
        SELECT t.region, COUNT(DISTINCT t.commune) as communes_centres
        FROM dw.dim_territoire t
        JOIN dw.dim_centres_service cs ON t.id_territoire = cs.id_territoire
        GROUP BY t.region
    )
    SELECT 
        ct.region,
        ct.total_communes as communes_totales,
        COALESCE(cac.communes_centres, 0) as communes_actives,
        ROUND((COALESCE(cac.communes_centres, 0)::NUMERIC / NULLIF(ct.total_communes, 0)) * 100, 2) as taux_couverture_pct
    FROM communes_totales ct
    LEFT JOIN communes_avec_centre cac ON ct.region = cac.region
    ORDER BY taux_couverture_pct DESC;
    """
    return execute_query(query)

def get_kpi_004_equite():
    """KPI-004: Ratio Équité d'Accès (Spec: Ratio Population/Centre)"""
    query = """
    WITH region_stats AS (
        SELECT 
            t.region,
            COUNT(DISTINCT cs.id_centre)::INTEGER as nombre_centres,
            SUM(DISTINCT COALESCE(s.population, 0))::BIGINT as population_totale
        FROM dw.dim_territoire t
        LEFT JOIN dw.dim_centres_service cs ON t.id_territoire = cs.id_territoire
        LEFT JOIN dw.dim_socioeconomique s ON t.id_territoire = s.id_territoire
        GROUP BY t.region
    ),
    ratios AS (
        SELECT 
            region, nombre_centres, population_totale,
            CASE WHEN nombre_centres > 0 THEN population_totale::FLOAT / nombre_centres ELSE 0 END as pop_par_centre
        FROM region_stats
    )
    SELECT 
        region, nombre_centres, population_totale,
        ROUND(pop_par_centre::NUMERIC, 0) as hab_par_centre,
        ROUND((pop_par_centre / NULLIF(MIN(CASE WHEN pop_par_centre > 0 THEN pop_par_centre END) OVER (), 0))::NUMERIC, 2) as ratio_inegalite
    FROM ratios
    ORDER BY pop_par_centre DESC;
    """
    return execute_query(query)

def get_kpi_005_rejet_global(region=None, prefecture=None, type_doc=None):
    """KPI-005: Taux de Rejet (Spec: Rejetées / (Validées + Rejetées))"""
    where_clause = "WHERE 1=1"
    if region and region != "Toutes":
        where_clause += f" AND t.region = '{region}'"
    if prefecture and prefecture != "Toutes":
        where_clause += f" AND t.prefecture = '{prefecture}'"
    if type_doc and type_doc != "Tous":
        where_clause += f" AND td.type_document = '{type_doc}'"

    query = f"""
    SELECT 
        COUNT(CASE WHEN f.statut_demande = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees,
        COUNT(CASE WHEN f.statut_demande = 'Validée' THEN 1 END)::INTEGER as demandes_validees,
        ROUND((COUNT(CASE WHEN f.statut_demande = 'Rejetée' THEN 1 END)::NUMERIC / 
               NULLIF(COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END), 0)) * 100, 2) as taux_rejet_global_pct
    FROM dw.fact_demandes f
    JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
    JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
    {where_clause};
    """
    return execute_query(query)

def get_kpi_005_rejet_par_type():
    """KPI-005: Taux de Rejet (Par Type de Document)"""
    query = """
    SELECT td.type_document,
        COUNT(CASE WHEN f.statut_demande = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees,
        COUNT(CASE WHEN f.statut_demande = 'Validée' THEN 1 END)::INTEGER as demandes_validees,
        ROUND((COUNT(CASE WHEN f.statut_demande = 'Rejetée' THEN 1 END)::NUMERIC / 
               NULLIF(COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END), 0)) * 100, 2) as taux_rejet_pct
    FROM dw.fact_demandes f
    JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
    GROUP BY td.type_document ORDER BY taux_rejet_pct DESC;
    """
    return execute_query(query)

def get_kpi_006_charge_par_region():
    """KPI-006: Charge de Travail par Agent (Demandes Traitées / Agents)"""
    query = """
    SELECT t.region, 
        COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END)::INTEGER as total_traite,
        SUM(DISTINCT cs.personnel_capacite_jour)::INTEGER as total_agents,
        ROUND(COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END)::NUMERIC / 
              NULLIF(SUM(DISTINCT cs.personnel_capacite_jour), 0), 2) as charge_par_agent
    FROM dw.dim_territoire t
    JOIN dw.fact_demandes f ON t.id_territoire = f.id_territoire
    JOIN dw.dim_centres_service cs ON t.id_territoire = cs.id_territoire
    GROUP BY t.region ORDER BY charge_par_agent DESC;
    """
    return execute_query(query)

def get_kpi_007_perf_type_document():
    """KPI-007: Performance par Type de Document"""
    query = """
    SELECT td.type_document,
        COUNT(f.id_fact)::INTEGER as nombre_demandes,
        ROUND(AVG(f.delai_traitement_jours)::NUMERIC, 2) as delai_moyen_jours,
        ROUND((COUNT(CASE WHEN f.statut_demande = 'Rejetée' THEN 1 END)::NUMERIC / 
               NULLIF(COUNT(CASE WHEN f.statut_demande IN ('Validée', 'Rejetée') THEN 1 END), 0)) * 100, 2) as taux_rejet_pct
    FROM dw.fact_demandes f
    JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
    GROUP BY td.type_document ORDER BY delai_moyen_jours DESC;
    """
    return execute_query(query)

def get_kpi_008_saturation_region():
    """KPI-008: Taux de Saturation (En Attente / Capacité Quotidienne)"""
    query = """
    SELECT t.region, 
        COUNT(CASE WHEN f.statut_demande = 'En Attente' THEN 1 END)::INTEGER as en_attente,
        SUM(DISTINCT cs.personnel_capacite_jour)::INTEGER as capacite_jour,
        ROUND((COUNT(CASE WHEN f.statut_demande = 'En Attente' THEN 1 END)::NUMERIC / 
              NULLIF(SUM(DISTINCT cs.personnel_capacite_jour), 0)) * 100, 2) as taux_saturation_pct
    FROM dw.dim_territoire t
    JOIN dw.fact_demandes f ON t.id_territoire = f.id_territoire
    JOIN dw.dim_centres_service cs ON t.id_territoire = cs.id_territoire
    GROUP BY t.region ORDER BY taux_saturation_pct DESC;
    """
    return execute_query(query)

def get_document_types():
    """Récupère les types de documents"""
    query = "SELECT DISTINCT type_document FROM dw.dim_type_document ORDER BY type_document;"
    df = execute_query(query)
    return df['type_document'].tolist() if not df.empty else []

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
    df = execute_query(query)
    # Si pas de coordonnées dans la DB, on utilise un mapping par défaut pour la démo
    if df.empty or df['lat'].isnull().all():
        mapping_coords = {
            'Maritime': (6.13, 1.22),
            'Plateaux': (7.5, 1.1),
            'Centrale': (8.5, 1.1),
            'Kara': (9.5, 1.2),
            'Savanes': (10.5, 0.5)
        }
        query_centres = "SELECT cs.nom_centre, cs.type_centre, t.region, t.prefecture FROM dw.dim_centres_service cs JOIN dw.dim_territoire t ON cs.id_territoire = t.id_territoire"
        df = execute_query(query_centres)
        if not df.empty:
            df['lat'] = df['region'].map(lambda x: mapping_coords.get(x, (6.1, 1.1))[0])
            df['lon'] = df['region'].map(lambda x: mapping_coords.get(x, (6.1, 1.1))[1])
    return df

def get_kpi_tendence_temporelle(region=None, type_doc=None):
    """Tendance mensuelle des demandes"""
    where_clause = "WHERE 1=1"
    if region and region != "Toutes":
        where_clause += f" AND t.region = '{region}'"
    if type_doc and type_doc != "Tous":
        where_clause += f" AND td.type_document = '{type_doc}'"
        
    query = f"""
    SELECT 
        f.annee_demande,
        f.mois_demande,
        TO_CHAR(MIN(f.date_demande), 'Month') as mois_nom,
        COUNT(*) as nb_demandes,
        ROUND(AVG(f.delai_traitement_jours)::NUMERIC, 2) as delai_moyen
    FROM dw.fact_demandes f
    JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
    JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
    {where_clause}
    GROUP BY f.annee_demande, f.mois_demande
    ORDER BY f.annee_demande, f.mois_demande;
    """
    return execute_query(query)

def get_kpi_centres_capacite_demande():
    """Capacité vs Demande par Centre (KPI-008 extended)"""
    query = """
    WITH demande_par_centre AS (
        SELECT 
            cs.nom_centre,
            COUNT(f.id_fact)::NUMERIC / NULLIF(COUNT(DISTINCT f.date_demande), 0) as demande_quotidienne_moyenne
        FROM dw.fact_demandes f
        JOIN dw.dim_centres_service cs ON f.id_territoire = cs.id_territoire
        GROUP BY cs.nom_centre
    )
    SELECT 
        cs.nom_centre,
        cs.personnel_capacite_jour as capacite_quotidienne,
        ROUND(COALESCE(d.demande_quotidienne_moyenne, 0), 2) as demande_quotidienne_estimee
    FROM dw.dim_centres_service cs
    LEFT JOIN demande_par_centre d ON cs.nom_centre = d.nom_centre
    ORDER BY demande_quotidienne_estimee DESC;
    """
    return execute_query(query)

def get_zones_prioritaires():
    """Identifie les zones sous-desservies (Forte population, faible couverture)"""
    query = """
    WITH stats_territoire AS (
        SELECT 
            t.region, t.prefecture,
            SUM(s.population) as population_totale,
            COUNT(DISTINCT cs.id_centre) as nb_centres
        FROM dw.dim_territoire t
        JOIN dw.dim_socioeconomique s ON t.id_territoire = s.id_territoire
        LEFT JOIN dw.dim_centres_service cs ON t.id_territoire = cs.id_territoire
        GROUP BY t.region, t.prefecture
    )
    SELECT 
        region, prefecture, population_totale, nb_centres,
        ROUND(population_totale::NUMERIC / NULLIF(nb_centres, 0), 0) as hab_par_centre
    FROM stats_territoire
    ORDER BY hab_par_centre DESC NULLS FIRST
    LIMIT 10;
    """
    return execute_query(query)

def get_centres_list():
    """Liste de tous les centres"""
    query = "SELECT DISTINCT nom_centre FROM dw.dim_centres_service WHERE nom_centre IS NOT NULL ORDER BY nom_centre;"
    df = execute_query(query)
    return df['nom_centre'].tolist() if not df.empty else []

def get_centre_details(nom_centre):
    """Fiche détaillée d'un centre"""
    query = f"""
    SELECT cs.*, t.region, t.prefecture, t.commune
    FROM dw.dim_centres_service cs
    JOIN dw.dim_territoire t ON cs.id_territoire = t.id_territoire
    WHERE cs.nom_centre = '{nom_centre}';
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

def page_accueil():
    """Page d'accueil"""
    st.title("Tableau de Bord - Services Publics Togo")
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
        st.subheader(" Délai Moyen par Région")
        df = get_kpi_001_dmt_par_region()
        if not df.empty:
            fig = px.bar(df, x='region', y='delai_moyen_jours', color='delai_moyen_jours',
                        color_continuous_scale="RdYlGn_r", title="DMT par Région")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Taux de Rejet par Type")
        df = get_kpi_005_rejet_par_type()
        if not df.empty:
            fig = px.bar(df.head(10), x='type_document', y='taux_rejet_pct',
                        color='taux_rejet_pct', color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)

def page_executive():
    """Vue Executive - Synthèse Décisionnelle"""
    st.title("Vue Executive - Synthèse")
    st.markdown("---")
    
    # Barre latérale pour les filtres globaux de la page
    with st.expander("Filtres Globaux", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            region = st.selectbox("Région", ["Toutes"] + get_regions())
        with col2:
            type_doc = st.selectbox("Type de Document", ["Tous"] + get_document_types())
        with col3:
            st.selectbox("Année", ["2023"])

    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    kpi_dmt = get_kpi_001_dmt_global(region, type_doc=type_doc)
    with col1:
        if not kpi_dmt.empty and kpi_dmt['delai_moyen_jours'].values[0] is not None:
            val = kpi_dmt['delai_moyen_jours'].values[0]
            st.metric("DMT Moyen", f"{val:.1f} j", delta=get_status_badge(val, "DMT"))
            
    kpi_abs = get_kpi_002_absorption_global(region)
    with col2:
        if not kpi_abs.empty:
            val = kpi_abs['taux_absorption_pct'].values[0]
            st.metric("Absorption", f"{val:.1f}%", delta=get_status_badge(val, "Absorption"))
            
    kpi_rej = get_kpi_005_rejet_global(region, type_doc=type_doc)
    with col3:
        if not kpi_rej.empty:
            val = kpi_rej['taux_rejet_global_pct'].values[0]
            st.metric("Taux de Rejet", f"{val:.1f}%", delta=get_status_badge(val, "Rejet"))
            
    with col4:
        total = kpi_abs['total_demandes'].values[0] if not kpi_abs.empty else 0
        st.metric("Volume de Demandes", f"{total:,}")

    st.markdown("---")
    
    # Analyse Temporelle
    st.subheader(" Tendance Temporelle (Volume & Performance)")
    df_trend = get_kpi_tendence_temporelle(region, type_doc)
    if not df_trend.empty:
        fig_trend = px.line(df_trend, x='mois_nom', y='nb_demandes', 
                           title="Evolution du nombre de demandes par mois",
                           markers=True, line_shape="spline",
                           labels={'nb_demandes': 'Volume', 'mois_nom': 'Mois'})
        st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Performance par Région")
        df_reg = get_kpi_002_absorption_par_region()
        fig_reg = px.bar(df_reg, x='region', y='taux_absorption_pct', color='taux_absorption_pct',
                        color_continuous_scale="RdYlGn")
        st.plotly_chart(fig_reg, use_container_width=True)
    
    with col2:
        st.subheader("Performance par Type de Document")
        df_type = get_kpi_007_perf_type_document()
        fig_type = px.bar(df_type, x='type_document', y='delai_moyen_jours', color='taux_rejet_pct',
                         color_continuous_scale="YlOrRd")
        st.plotly_chart(fig_type, use_container_width=True)

def page_operationnelle():
    """Vue Opérationnelle - Pilotage par Centre"""
    st.title("Vue Opérationnelle")
    st.markdown("---")
    
    # Système d'onglets pour une meilleure organisation
    tab_perf, tab_centre = st.tabs([" Performance Globale", " Zoom par Centre"])
    
    with tab_perf:
        metric = st.selectbox("Indicateur Opérationnel", ["Saturation", "Charge", "Capacité des Centres"])
        st.markdown("---")
        
        if metric == "Saturation":
            st.subheader("Saturation par Région (Demandes en Attente / Capacité)")
            df = get_kpi_008_saturation_region()
            if not df.empty:
                fig = px.bar(df, x='region', y='taux_saturation_pct',
                            color='taux_saturation_pct', color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df)
    
        elif metric == "Charge":
            st.subheader("Charge de Travail par Région (Demandes Traitées / Agent)")
            df = get_kpi_006_charge_par_region()
            if not df.empty:
                fig = px.bar(df, x='region', y='charge_par_agent',
                            color='charge_par_agent', color_continuous_scale="Oranges")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df)

        elif metric == "Capacité des Centres":
            st.subheader("Analyse Capacité vs Demande Quotidienne")
            st.info("Comparaison entre la capacité théorique (agents) et la demande moyenne réelle observée par jour.")
            df = get_kpi_centres_capacite_demande()
            if not df.empty:
                # Création d'un graphique comparatif
                fig = px.bar(df.head(20), x='nom_centre', y=['capacite_quotidienne', 'demande_quotidienne_estimee'],
                            barmode='group', title="Top 20 Centres : Capacité vs Demande (Quotidien)")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df)

    with tab_centre:
        st.subheader("🔎 Fiche d'Identité du Centre")
        centre_sel = st.selectbox("Sélectionnez un centre :", get_centres_list())
        if centre_sel:
            det = get_centre_details(centre_sel)
            if not det.empty:
                d = det.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Capacité (Agents)", d['personnel_capacite_jour'])
                c2.metric("Guichets", d['nombre_guichets'])
                c3.metric("Numérique", d['equipement_numerique'])
                c4.metric("Statut", d['statut_centre'])
                
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.write(f"**📍 Localisation :** {d['region']}, {d['prefecture']}, {d['commune']}")
                with info_col2:
                    st.write(f"**⏰ Heures :** {d['heures_ouverture']}")
                    st.write(f"**📅 Date Ouverture :** {d.get('date_ouverture', 'N/A')}")

def page_territoriale():
    """Vue Territoriale"""
    st.title("Vue Territoriale")
    st.markdown("---")
    
    metric = st.selectbox("Analyse", ["Couverture", "Équité", "Zones Sous-desservies", "Performance Document", "Rejet"])
    
    st.markdown("---")
    
    if metric == "Couverture":
        st.subheader("Analyse de la Couverture Territoriale")
        df_carto = get_centres_carto()
        if not df_carto.empty:
            st.markdown("### Carte des Centres de Service")
            fig_map = px.scatter_mapbox(df_carto, lat="lat", lon="lon", 
                                       hover_name="nom_centre", 
                                       hover_data=["region", "prefecture", "type_centre"],
                                       color="type_centre", zoom=5.8, height=700)
            
            fig_map.update_layout(
                mapbox_style="carto-positron",
                mapbox_center={"lat": 8.7, "lon": 1.2},
                margin={"r":0,"t":40,"l":0,"b":0}
            )
            st.plotly_chart(fig_map, use_container_width=True)

        df = get_kpi_003_couverture()
        if not df.empty:
            fig = px.bar(df, x='region', y='taux_couverture_pct', color='taux_couverture_pct')
            st.plotly_chart(fig, use_container_width=True)

    elif metric == "Zones Sous-desservies":
        st.subheader("🚀 Top 10 des Zones Prioritaires")
        df_prior = get_zones_prioritaires()
        if not df_prior.empty:
            fig = px.bar(df_prior, x='prefecture', y='hab_par_centre', color='region',
                        title="Nombre d'habitants par centre")
            st.plotly_chart(fig, use_container_width=True)
            st.table(df_prior)

    elif metric == "Équité":
        st.subheader("Équité d'Accès - Ratio Population / Centre")
        df = get_kpi_004_equite()
        if not df.empty:
            fig = px.bar(df, x='region', y='hab_par_centre', color='ratio_inegalite',
                        labels={'hab_par_centre': 'Habitants pour 1 centre', 'ratio_inegalite': 'Ratio Inégalité'})
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
            
    elif metric == "Performance Document":
        st.subheader("Performance par Type de Document")
        df = get_kpi_007_perf_type_document()
        if not df.empty:
            fig = px.bar(df, x='type_document', y='delai_moyen_jours', color='taux_rejet_pct')
            st.plotly_chart(fig, use_container_width=True)

    elif metric == "Rejet":
        st.subheader("Taux de Rejet par Type de Document")
        df = get_kpi_005_rejet_par_type()
        if not df.empty:
            fig = px.bar(df.head(15), x='type_document', y='taux_rejet_pct', color='taux_rejet_pct')
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Fonction principale"""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Sélectionnez une vue:",
        ["Accueil", "Executive", "Opérationnelle", "Territoriale"])
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Actualisation: {datetime.now().strftime('%H:%M:%S')}")
    
    if page == "Accueil":
        page_accueil()
    elif page == "Executive":
        page_executive()
    elif page == "Opérationnelle":
        page_operationnelle()
    elif page == "Territoriale":
        page_territoriale()

if __name__ == "__main__":
    main()

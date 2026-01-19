-- Script 5: Vues analytiques
-- =====================================================
\c service_public_db;

\echo '📊 Création des vues analytiques...';

-- ========================================
-- VUE 1: Résumé par Région
-- ========================================
CREATE OR REPLACE VIEW dw.v_resume_region AS
SELECT 
    t.region,
    COUNT(DISTINCT f.id_fact) as nombre_demandes,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen_jours,
    ROUND(AVG(f.taux_rejet)::numeric, 2) as taux_rejet_moyen,
    COUNT(DISTINCT t.id_territoire) as nombre_territoires,
    COUNT(DISTINCT CASE WHEN c.statut_centre = 'Actif' THEN c.id_centre END) as centres_actifs
FROM dw.fact_demandes f
JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
LEFT JOIN dw.dim_centres_service c ON t.id_territoire = c.id_territoire
GROUP BY t.region
ORDER BY total_demandes DESC;

-- ========================================
-- VUE 2: Performance des Centres
-- ========================================
CREATE OR REPLACE VIEW dw.v_performance_centres AS
SELECT 
    t.region,
    cs.nom_centre,
    cs.type_centre,
    cs.personnel_capacite_jour,
    cs.nombre_guichets,
    cs.statut_centre,
    COUNT(DISTINCT f.id_fact) as nombre_demandes_traitees,
    SUM(f.nombre_demandes) as volume_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen
FROM dw.dim_centres_service cs
JOIN dw.dim_territoire t ON cs.id_territoire = t.id_territoire
LEFT JOIN dw.fact_demandes f ON t.id_territoire = f.id_territoire
GROUP BY t.region, cs.id_centre, cs.nom_centre, cs.type_centre, cs.personnel_capacite_jour, cs.nombre_guichets, cs.statut_centre
ORDER BY t.region, volume_demandes DESC;

-- ========================================
-- VUE 3: Indicateurs Socio-économiques
-- ========================================
CREATE OR REPLACE VIEW dw.v_indicateurs_socio AS
SELECT 
    t.region,
    COUNT(DISTINCT s.id_socio) as nombre_communes,
    ROUND(AVG(s.population)::numeric, 0) as population_moyenne,
    ROUND(AVG(s.densite)::numeric, 2) as densite_moyenne,
    ROUND(AVG(s.taux_urbanisation)::numeric, 3) as urbanisation_moyenne,
    ROUND(AVG(s.taux_alphabetisation)::numeric, 3) as alphabetisation_moyenne,
    ROUND(AVG(s.age_median)::numeric, 1) as age_median_moyen,
    ROUND(AVG(s.revenu_moyen_fcfa)::numeric, 0) as revenu_moyen_fcfa
FROM dw.dim_socioeconomique s
JOIN dw.dim_territoire t ON s.id_territoire = t.id_territoire
GROUP BY t.region
ORDER BY t.region;

-- ========================================
-- VUE 4: Analyse par Type de Document
-- ========================================
CREATE OR REPLACE VIEW dw.v_analyse_documents AS
SELECT 
    td.type_document,
    td.categorie_document,
    COUNT(DISTINCT f.id_fact) as nombre_enregistrements,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen,
    COUNT(DISTINCT CASE WHEN f.statut_demande = 'Traitee' THEN f.id_fact END) as demandes_traitees,
    COUNT(DISTINCT CASE WHEN f.statut_demande = 'Rejetee' THEN f.id_fact END) as demandes_rejetees
FROM dw.fact_demandes f
JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
GROUP BY td.id_type_document, td.type_document, td.categorie_document
ORDER BY total_demandes DESC;

-- ========================================
-- VUE 5: Tendance Temporelle
-- ========================================
CREATE OR REPLACE VIEW dw.v_tendance_temporelle AS
SELECT 
    f.annee_demande,
    f.mois_demande,
    f.jour_semaine_demande,
    COUNT(DISTINCT f.id_fact) as nombre_types,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen,
    ROUND((SUM(f.nombre_demandes)::numeric / NULLIF(COUNT(DISTINCT f.id_fact), 0))::numeric, 2) as demandes_par_type
FROM dw.fact_demandes f
GROUP BY f.annee_demande, f.mois_demande, f.jour_semaine_demande
ORDER BY f.annee_demande DESC, f.mois_demande DESC;

-- ========================================
-- VUE 6: Analyse Géographique
-- ========================================
CREATE OR REPLACE VIEW dw.v_analyse_geographique AS
SELECT 
    t.region,
    t.prefecture,
    t.commune,
    t.latitude,
    t.longitude,
    COUNT(DISTINCT f.id_fact) as nombre_demandes,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    s.population,
    s.densite,
    ROUND((SUM(f.nombre_demandes)::numeric / NULLIF(s.population, 0) * 1000)::numeric, 2) as demandes_pour_1000_hab
FROM dw.fact_demandes f
JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
LEFT JOIN dw.dim_socioeconomique s ON t.id_territoire = s.id_territoire
GROUP BY t.region, t.prefecture, t.commune, t.latitude, t.longitude, s.population, s.densite
ORDER BY total_demandes DESC;

-- ========================================
-- VUE 7: Tableau de Bord Principal
-- ========================================
CREATE OR REPLACE VIEW dw.v_tableau_bord_principal AS
SELECT 
    (SELECT SUM(nombre_demandes) FROM dw.fact_demandes) as total_demandes_globales,
    (SELECT COUNT(DISTINCT id_territoire) FROM dw.fact_demandes) as territoires_couverts,
    (SELECT COUNT(DISTINCT id_centre) FROM dw.dim_centres_service) as nombre_centres,
    (SELECT COUNT(DISTINCT id_type_document) FROM dw.fact_demandes) as types_documents,
    (SELECT ROUND(AVG(delai_traitement_jours)::numeric, 2) FROM dw.fact_demandes) as delai_moyen_global,
    (SELECT ROUND(AVG(taux_rejet)::numeric, 3) FROM dw.fact_demandes) as taux_rejet_global,
    (SELECT COUNT(*) FROM dw.dim_territoire WHERE region IS NOT NULL) as regions_actives,
    CURRENT_TIMESTAMP as date_rafraichissement;

\echo '✅ Vues analytiques créées avec succès!';
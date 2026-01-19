-- Script 07: Requêtes analytiques avancées
-- =====================================================
\c service_public_db;

\echo '📊 REQUÊTES ANALYTIQUES AVANCÉES';
\echo '════════════════════════════════════════════════════════════';

-- ========================================
-- ANALYSE 1: KPI Globaux
-- ========================================
\echo '';
\echo '1️⃣ KPI GLOBAUX';

SELECT * FROM dw.v_tableau_bord_principal;

-- ========================================
-- ANALYSE 2: Top 10 Communes par volume de demandes
-- ========================================
\echo '';
\echo '2️⃣ TOP 10 COMMUNES PAR VOLUME';

SELECT 
    t.region,
    t.prefecture,
    t.commune,
    SUM(f.nombre_demandes) as total_demandes,
    COUNT(DISTINCT f.id_fact) as nombre_enregistrements,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen,
    s.population,
    ROUND((SUM(f.nombre_demandes)::numeric / NULLIF(s.population, 0) * 1000)::numeric, 2) as demandes_pour_1000_hab
FROM dw.fact_demandes f
JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
LEFT JOIN dw.dim_socioeconomique s ON t.id_territoire = s.id_territoire
GROUP BY t.region, t.prefecture, t.commune, s.population
ORDER BY total_demandes DESC
LIMIT 10;

-- ========================================
-- ANALYSE 3: Performance par type de centre
-- ========================================
\echo '';
\echo '3️⃣ PERFORMANCE PAR TYPE DE CENTRE';

SELECT 
    cs.type_centre,
    COUNT(DISTINCT cs.id_centre) as nombre_centres,
    COUNT(DISTINCT CASE WHEN cs.statut_centre = 'Actif' THEN cs.id_centre END) as centres_actifs,
    ROUND(AVG(cs.personnel_capacite_jour)::numeric, 0) as capacite_moyenne,
    ROUND(AVG(cs.nombre_guichets)::numeric, 1) as guichets_moyens,
    COUNT(DISTINCT f.id_fact) as demandes_traitees,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen
FROM dw.dim_centres_service cs
LEFT JOIN dw.dim_territoire t ON cs.id_territoire = t.id_territoire
LEFT JOIN dw.fact_demandes f ON t.id_territoire = f.id_territoire
GROUP BY cs.type_centre
ORDER BY nombre_centres DESC;

-- ========================================
-- ANALYSE 4: Tendance temporelle (mois à mois)
-- ========================================
\echo '';
\echo '4️⃣ TENDANCE TEMPORELLE (MOIS À MOIS)';

SELECT 
    f.annee_demande,
    f.mois_demande,
    TO_CHAR(TO_DATE(f.mois_demande::text, 'MM'), 'Month') as nom_mois,
    SUM(f.nombre_demandes) as total_demandes,
    COUNT(DISTINCT f.id_fact) as nombre_types,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen,
    LAG(SUM(f.nombre_demandes)) OVER (ORDER BY f.annee_demande, f.mois_demande) as demandes_mois_precedent
FROM dw.fact_demandes f
GROUP BY f.annee_demande, f.mois_demande
ORDER BY f.annee_demande DESC, f.mois_demande DESC;

-- ========================================
-- ANALYSE 5: Analyse démographique vs Demandes
-- ========================================
\echo '';
\echo '5️⃣ CORRÉLATION DÉMOGRAPHIE vs DEMANDES';

SELECT 
    t.region,
    COUNT(DISTINCT t.id_territoire) as nombre_territoires,
    ROUND(AVG(s.population)::numeric, 0) as population_moyenne,
    ROUND(AVG(s.densite)::numeric, 1) as densite_moyenne,
    ROUND(AVG(s.taux_alphabetisation)::numeric, 3) as alphabetisation_moyenne,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND((SUM(f.nombre_demandes)::numeric / NULLIF(ROUND(AVG(s.population)::numeric, 0), 0) * 1000)::numeric, 2) as demandes_pour_1000_hab
FROM dw.fact_demandes f
JOIN dw.dim_territoire t ON f.id_territoire = t.id_territoire
LEFT JOIN dw.dim_socioeconomique s ON t.id_territoire = s.id_territoire
GROUP BY t.region
ORDER BY total_demandes DESC;

-- ========================================
-- ANALYSE 6: Documents problématiques (délais/rejets élevés)
-- ========================================
\echo '';
\echo '6️⃣ DOCUMENTS PROBLÉMATIQUES (DÉLAIS/REJETS ÉLEVÉS)';

SELECT 
    td.type_document,
    td.categorie_document,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen_jours,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen,
    COUNT(DISTINCT CASE WHEN f.delai_traitement_jours > 30 THEN f.id_fact END) as demandes_delai_long,
    COUNT(DISTINCT CASE WHEN f.taux_rejet > 0.2 THEN f.id_fact END) as demandes_rejet_eleve
FROM dw.fact_demandes f
JOIN dw.dim_type_document td ON f.id_type_document = td.id_type_document
GROUP BY td.id_type_document, td.type_document, td.categorie_document
HAVING AVG(f.delai_traitement_jours) > 10 OR AVG(f.taux_rejet) > 0.1
ORDER BY delai_moyen_jours DESC;

-- ========================================
-- ANALYSE 7: Distribution par jour de la semaine
-- ========================================
\echo '';
\echo '7️⃣ DISTRIBUTION PAR JOUR DE LA SEMAINE';

SELECT 
    f.jour_semaine_demande,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen,
    COUNT(DISTINCT f.id_fact) as nombre_types
FROM dw.fact_demandes f
WHERE f.jour_semaine_demande IS NOT NULL
GROUP BY f.jour_semaine_demande
ORDER BY 
    CASE 
        WHEN f.jour_semaine_demande = 'Monday' THEN 1
        WHEN f.jour_semaine_demande = 'Tuesday' THEN 2
        WHEN f.jour_semaine_demande = 'Wednesday' THEN 3
        WHEN f.jour_semaine_demande = 'Thursday' THEN 4
        WHEN f.jour_semaine_demande = 'Friday' THEN 5
        WHEN f.jour_semaine_demande = 'Saturday' THEN 6
        WHEN f.jour_semaine_demande = 'Sunday' THEN 7
    END;

-- ========================================
-- ANALYSE 8: Demandes par canal d'accès
-- ========================================
\echo '';
\echo '8️⃣ ANALYSE PAR CANAL D\'ACCÈS';

SELECT 
    f.canal_demande,
    SUM(f.nombre_demandes) as total_demandes,
    COUNT(DISTINCT f.id_fact) as nombre_types,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen,
    COUNT(DISTINCT CASE WHEN f.statut_demande = 'Traitee' THEN f.id_fact END) as demandes_traitees,
    ROUND((COUNT(DISTINCT CASE WHEN f.statut_demande = 'Traitee' THEN f.id_fact END)::numeric / 
            NULLIF(COUNT(DISTINCT f.id_fact), 0) * 100)::numeric, 2) as taux_traitement_pourcent
FROM dw.fact_demandes f
WHERE f.canal_demande IS NOT NULL
GROUP BY f.canal_demande
ORDER BY total_demandes DESC;

-- ========================================
-- ANALYSE 9: Profil des demandeurs
-- ========================================
\echo '';
\echo '9️⃣ PROFIL DES DEMANDEURS (ÂGE ET SEXE)';

SELECT 
    CASE 
        WHEN f.age_demandeur IS NULL THEN 'Non renseigné'
        WHEN f.age_demandeur < 25 THEN '< 25 ans'
        WHEN f.age_demandeur < 40 THEN '25-40 ans'
        WHEN f.age_demandeur < 60 THEN '40-60 ans'
        ELSE '> 60 ans'
    END as groupe_age,
    f.sexe_demandeur,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND(AVG(f.delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(f.taux_rejet)::numeric, 3) as taux_rejet_moyen
FROM dw.fact_demandes f
GROUP BY groupe_age, f.sexe_demandeur
ORDER BY groupe_age, f.sexe_demandeur;

-- ========================================
-- ANALYSE 10: Régions les moins bien dotées
-- ========================================
\echo '';
\echo '🔟 RÉGIONS LES MOINS BIEN DOTÉES (RESSOURCES vs DEMANDES)';

SELECT 
    t.region,
    COUNT(DISTINCT cs.id_centre) as nombre_centres,
    SUM(cs.personnel_capacite_jour) as capacite_totale,
    SUM(f.nombre_demandes) as total_demandes,
    ROUND((SUM(cs.personnel_capacite_jour)::numeric / NULLIF(SUM(f.nombre_demandes), 0))::numeric, 2) as personnel_par_demande,
    ROUND((SUM(f.nombre_demandes)::numeric / NULLIF(SUM(cs.personnel_capacite_jour), 0))::numeric, 2) as demandes_par_personnel
FROM dw.dim_territoire t
LEFT JOIN dw.dim_centres_service cs ON t.id_territoire = cs.id_territoire
LEFT JOIN dw.fact_demandes f ON t.id_territoire = f.id_territoire
GROUP BY t.region
ORDER BY demandes_par_personnel DESC;

\echo '';
\echo '════════════════════════════════════════════════════════════';
\echo '✅ REQUÊTES ANALYTIQUES TERMINÉES';
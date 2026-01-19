-- Script 06: Maintenance et nettoyage des données
-- =====================================================
\c service_public_db;

\echo '🧹 Maintenance de la base de données...';

-- ========================================
-- PROCÉDURE 1: Vider et recharger les données
-- ========================================

-- Vider les tables DW (en respectant les FK)
TRUNCATE TABLE dw.fact_demandes CASCADE;
TRUNCATE TABLE dw.dim_centres_service CASCADE;
TRUNCATE TABLE dw.dim_communes CASCADE;
TRUNCATE TABLE dw.dim_socioeconomique CASCADE;
TRUNCATE TABLE dw.dim_type_document CASCADE;
TRUNCATE TABLE dw.dim_territoire CASCADE;

\echo '✅ Tables DW vidées';

-- Vider les tables RAW
TRUNCATE TABLE raw.demandes_services_public CASCADE;
TRUNCATE TABLE raw.centres_service CASCADE;
TRUNCATE TABLE raw.communes CASCADE;
TRUNCATE TABLE raw.donnees_socioeconomiques CASCADE;

\echo '✅ Tables RAW vidées';

-- ========================================
-- PROCÉDURE 2: Vérifier l'intégrité
-- ========================================

-- Vérifier les contraintes d'unicité
\echo '';
\echo '🔍 Vérification des contraintes d\'unicité...';

-- Compter les doublons potentiels dans RAW
SELECT 'Doublons centres_service' as check_name, COUNT(*) as doublon_count 
FROM raw.centres_service 
GROUP BY centre_id 
HAVING COUNT(*) > 1;

SELECT 'Doublons demandes' as check_name, COUNT(*) as doublon_count 
FROM raw.demandes_services_public 
GROUP BY demande_id 
HAVING COUNT(*) > 1;

\echo '✅ Vérification terminée';

-- ========================================
-- PROCÉDURE 3: Statistiques de qualité
-- ========================================

\echo '';
\echo '📊 Statistiques de qualité des données RAW:';

SELECT 
    'Communes' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT commune) as communes_uniques,
    COUNT(DISTINCT region) as regions_uniques,
    COUNT(CASE WHEN commune IS NULL THEN 1 END) as valeurs_null
FROM raw.communes
UNION ALL
SELECT 
    'Centres Service',
    COUNT(*),
    COUNT(DISTINCT centre_id),
    COUNT(DISTINCT region),
    COUNT(CASE WHEN centre_id IS NULL THEN 1 END)
FROM raw.centres_service
UNION ALL
SELECT 
    'Demandes',
    COUNT(*),
    COUNT(DISTINCT demande_id),
    COUNT(DISTINCT type_document),
    COUNT(CASE WHEN demande_id IS NULL THEN 1 END)
FROM raw.demandes_services_public
UNION ALL
SELECT 
    'Socio-économiques',
    COUNT(*),
    COUNT(DISTINCT commune),
    COUNT(DISTINCT region),
    COUNT(CASE WHEN commune IS NULL THEN 1 END)
FROM raw.donnees_socioeconomiques;

-- ========================================
-- PROCÉDURE 4: Optimisation des index
-- ========================================

\echo '';
\echo '🔧 Réindexation des index...';

REINDEX INDEX CONCURRENTLY idx_dim_territoire_region;
REINDEX INDEX CONCURRENTLY idx_dim_territoire_commune;
REINDEX INDEX CONCURRENTLY idx_fact_demandes_territoire;
REINDEX INDEX CONCURRENTLY idx_fact_demandes_date;
REINDEX INDEX CONCURRENTLY idx_fact_demandes_type;
REINDEX INDEX CONCURRENTLY idx_dim_centres_territoire;
REINDEX INDEX CONCURRENTLY idx_dim_communes_territoire;

\echo '✅ Réindexation terminée';

-- ========================================
-- PROCÉDURE 5: Analyser les tables
-- ========================================

\echo '';
\echo '📈 Analyse des tables (VACUUM ANALYZE)...';

VACUUM ANALYZE raw.communes;
VACUUM ANALYZE raw.centres_service;
VACUUM ANALYZE raw.demandes_services_public;
VACUUM ANALYZE raw.donnees_socioeconomiques;

VACUUM ANALYZE dw.dim_territoire;
VACUUM ANALYZE dw.dim_communes;
VACUUM ANALYZE dw.dim_centres_service;
VACUUM ANALYZE dw.dim_type_document;
VACUUM ANALYZE dw.dim_socioeconomique;
VACUUM ANALYZE dw.fact_demandes;

\echo '✅ Analyse terminée';

-- ========================================
-- PROCÉDURE 6: Rapport final
-- ========================================

\echo '';
\echo '═══════════════════════════════════════════════════════════';
\echo '📋 RAPPORT DE MAINTENANCE';
\echo '═══════════════════════════════════════════════════════════';

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as taille_totale
FROM pg_tables
WHERE schemaname IN ('raw', 'dw')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

\echo '═══════════════════════════════════════════════════════════';
\echo '✅ MAINTENANCE TERMINÉE';
\echo '═══════════════════════════════════════════════════════════';
-- Script 4: Transformation des données RAW → DW
-- =====================================================
\c service_public_db;

\echo '🔄 Transformation des données du RAW vers le DW...';

-- ========================================
-- ÉTAPE 1: Remplir la Dimension TERRITOIRE
-- ========================================

-- ÉTAPE 1: Remplir la Dimension TERRITOIRE (Union de toutes les sources)
INSERT INTO dw.dim_territoire (region, prefecture, commune, quartier, latitude, longitude, code_postal)
-- De centres_service
SELECT DISTINCT region, prefecture, commune, quartier, latitude, longitude, NULL::VARCHAR FROM raw.centres_service
WHERE region IS NOT NULL AND prefecture IS NOT NULL AND commune IS NOT NULL
UNION
-- De demandes
SELECT DISTINCT region, prefecture, commune, quartier, NULL::DECIMAL, NULL::DECIMAL, NULL::VARCHAR FROM raw.demandes_services_public
WHERE region IS NOT NULL AND prefecture IS NOT NULL AND commune IS NOT NULL
UNION
-- De communes
SELECT DISTINCT region, prefecture, commune, NULL::VARCHAR, latitude, longitude, code_postal FROM raw.communes
WHERE region IS NOT NULL AND prefecture IS NOT NULL AND commune IS NOT NULL
UNION
-- De socioeconomiques
SELECT DISTINCT region, prefecture, commune, NULL::VARCHAR, NULL::DECIMAL, NULL::DECIMAL, NULL::VARCHAR FROM raw.donnees_socioeconomiques
WHERE region IS NOT NULL AND prefecture IS NOT NULL AND commune IS NOT NULL
ON CONFLICT (region, prefecture, commune, quartier) DO NOTHING;

\echo '✅ Dimension TERRITOIRE remplie';

-- ========================================
-- ÉTAPE 2: Remplir la Dimension Type Document
-- ========================================

INSERT INTO dw.dim_type_document (type_document, categorie_document)
SELECT DISTINCT
    type_document,
    categorie_document
FROM raw.demandes_services_public
WHERE type_document IS NOT NULL
ON CONFLICT (type_document, categorie_document) DO NOTHING;

\echo '✅ Dimension TYPE_DOCUMENT remplie';

-- ========================================
-- ÉTAPE 3: Remplir la Dimension Communes
-- ========================================

INSERT INTO dw.dim_communes (id_territoire, commune_code, type_commune, altitude_m, superficie_km2, population_densite, distance_capitale_km, zone_climatique)
SELECT DISTINCT
    t.id_territoire,
    c.commune_id,
    c.type_commune,
    c.altitude_m,
    c.superficie_km2,
    c.population_densite,
    c.distance_capitale_km,
    c.zone_climatique
FROM raw.communes c
JOIN dw.dim_territoire t ON c.region = t.region 
                         AND c.prefecture = t.prefecture 
                         AND c.commune = t.commune
WHERE c.commune IS NOT NULL;

\echo '✅ Dimension COMMUNES remplie';

-- ========================================
-- ÉTAPE 4: Remplir la Dimension Centres de Service
-- ========================================

INSERT INTO dw.dim_centres_service (centre_code, id_territoire, nom_centre, type_centre, personnel_capacite_jour, nombre_guichets, heures_ouverture, horaire_nuit, equipement_numerique, date_ouverture, statut_centre)
SELECT DISTINCT
    c.centre_id,
    t.id_territoire,
    c.nom_centre,
    c.type_centre,
    c.personnel_capacite_jour,
    c.nombre_guichets,
    c.heures_ouverture,
    c.horaire_nuit,
    c.equipement_numerique,
    c.date_ouverture,
    c.statut_centre
FROM raw.centres_service c
JOIN dw.dim_territoire t ON c.region = t.region 
                         AND c.prefecture = t.prefecture 
                         AND c.commune = t.commune
                         AND COALESCE(c.quartier, '') = COALESCE(t.quartier, '')
WHERE c.centre_id IS NOT NULL;

\echo '✅ Dimension CENTRES_SERVICE remplie';

-- ========================================
-- ÉTAPE 5: Remplir la Dimension Socio-économique
-- ========================================

INSERT INTO dw.dim_socioeconomique (id_territoire, population, densite, taux_urbanisation, taux_alphabetisation, age_median, nombre_menages, revenu_moyen_fcfa)
SELECT DISTINCT
    t.id_territoire,
    s.population,
    s.densite,
    s.taux_urbanisation,
    s.taux_alphabetisation,
    s.age_median,
    s.nombre_menages,
    s.revenu_moyen_fcfa
FROM raw.donnees_socioeconomiques s
JOIN dw.dim_territoire t ON s.region = t.region 
                         AND s.prefecture = t.prefecture 
                         AND s.commune = t.commune
WHERE s.commune IS NOT NULL;

\echo '✅ Dimension SOCIOECONOMIQUE remplie';

-- ========================================
-- ÉTAPE 6: Remplir la Table de Faits Demandes
-- ========================================

INSERT INTO dw.fact_demandes (
    id_territoire, 
    id_type_document, 
    demande_code, 
    nombre_demandes, 
    delai_traitement_jours, 
    taux_rejet, 
    date_demande, 
    motif_demande, 
    statut_demande, 
    canal_demande, 
    age_demandeur, 
    sexe_demandeur, 
    annee_demande, 
    mois_demande, 
    jour_semaine_demande
)
SELECT
    t.id_territoire,
    td.id_type_document,
    d.demande_id,
    d.nombre_demandes,
    d.delai_traitement_jours,
    d.taux_rejet,
    d.date_demande,
    d.motif_demande,
    d.statut_demande,
    d.canal_demande,
    d.age_demandeur,
    d.sexe_demandeur,
    d.annee_demande,
    d.mois_demande,
    d.jour_semaine_demande
FROM raw.demandes_services_public d
JOIN dw.dim_territoire t ON d.region = t.region 
                         AND d.prefecture = t.prefecture 
                         AND d.commune = t.commune
                         AND COALESCE(d.quartier, '') = COALESCE(t.quartier, '')
JOIN dw.dim_type_document td ON d.type_document = td.type_document
                             AND COALESCE(d.categorie_document, '') = COALESCE(td.categorie_document, '')
WHERE d.demande_id IS NOT NULL;

\echo '✅ Table de Faits DEMANDES remplie';

-- ========================================
-- AFFICHER LES STATISTIQUES
-- ========================================

SELECT 
    'Territoire' as table_name,
    COUNT(*) as row_count
FROM dw.dim_territoire
UNION ALL
SELECT 'Type Document', COUNT(*) FROM dw.dim_type_document
UNION ALL
SELECT 'Communes', COUNT(*) FROM dw.dim_communes
UNION ALL
SELECT 'Centres Service', COUNT(*) FROM dw.dim_centres_service
UNION ALL
SELECT 'Socioeconomique', COUNT(*) FROM dw.dim_socioeconomique
UNION ALL
SELECT 'Faits Demandes', COUNT(*) FROM dw.fact_demandes;

\echo '✅ Transformation DATA WAREHOUSE terminée!';
-- Script 5: Requêtes d'analyse principales
-- =====================================================
\c service_public_db;

-- Requête 1: Demandes totales par région
SELECT 
    'Demandes totales par région' as analyse,
    region,
    SUM(nombre_demandes) as total_demandes,
    COUNT(DISTINCT centre_id) as centres_impliques
FROM demandes_services_public d
LEFT JOIN centres_service c ON d.commune = c.commune
GROUP BY region
ORDER BY total_demandes DESC;

-- Requête 2: Performance des centres
SELECT 
    'Performance centres de service' as analyse,
    region,
    COUNT(*) as nombre_centres,
    ROUND(AVG(personnel_capacite_jour)::numeric, 0) as capacite_moyenne,
    ROUND(AVG(nombre_guichets)::numeric, 1) as guichets_moyen,
    COUNT(CASE WHEN statut_centre = 'Actif' THEN 1 END) as centres_actifs
FROM centres_service
GROUP BY region
ORDER BY nombre_centres DESC;

-- Requête 3: Top 10 communes avec le plus de demandes
SELECT 
    'Top 10 communes' as analyse,
    commune,
    prefecture,
    region,
    SUM(nombre_demandes) as total_demandes,
    ROUND(AVG(delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(taux_rejet)::numeric, 3) as taux_rejet
FROM demandes_services_public
GROUP BY commune, prefecture, region
ORDER BY total_demandes DESC
LIMIT 10;

-- Requête 4: Analyse démographique vs demandes
SELECT 
    'Corrélation démographie-demandes' as analyse,
    d.region,
    s.population as population_region,
    SUM(d.nombre_demandes) as total_demandes,
    ROUND((SUM(d.nombre_demandes)::numeric / NULLIF(s.population, 0) * 1000)::numeric, 2) as demandes_pour_1000_habitants
FROM demandes_services_public d
LEFT JOIN donnees_socioeconomiques s ON d.region = s.region
GROUP BY d.region, s.population
ORDER BY demandes_pour_1000_habitants DESC;

-- Requête 5: Tendance temporelle
SELECT 
    'Évolution des demandes' as analyse,
    annee_demande,
    mois_demande,
    SUM(nombre_demandes) as total_demandes,
    COUNT(DISTINCT type_document) as types_documents,
    ROUND(AVG(delai_traitement_jours)::numeric, 2) as delai_moyen
FROM demandes_services_public
GROUP BY annee_demande, mois_demande
ORDER BY annee_demande DESC, mois_demande DESC;

-- Afficher un message de confirmation
\echo 'Requêtes d\'analyse disponibles!';

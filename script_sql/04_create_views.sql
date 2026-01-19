-- Script 4: Création de vues utiles pour l'analyse
-- =====================================================
\c service_public_db;

-- Vue 1: Résumé des demandes par région
CREATE OR REPLACE VIEW v_demandes_par_region AS
SELECT 
    region,
    COUNT(*) as nombre_demandes_types,
    SUM(nombre_demandes) as total_demandes,
    ROUND(AVG(delai_traitement_jours)::numeric, 2) as delai_moyen_jours,
    ROUND(AVG(taux_rejet)::numeric, 2) as taux_rejet_moyen,
    ROUND(AVG(taux_rejet)::numeric, 2) * 100 as taux_rejet_pourcent
FROM demandes_services_public
GROUP BY region
ORDER BY total_demandes DESC;

-- Vue 2: Performance des centres de service par région
CREATE OR REPLACE VIEW v_centres_par_region AS
SELECT 
    region,
    COUNT(*) as nombre_centres,
    SUM(personnel_capacite_jour) as capacite_total,
    SUM(nombre_guichets) as guichets_total,
    COUNT(CASE WHEN statut_centre = 'Actif' THEN 1 END) as centres_actifs
FROM centres_service
GROUP BY region
ORDER BY nombre_centres DESC;

-- Vue 3: Indicateurs socio-économiques par région
CREATE OR REPLACE VIEW v_socio_par_region AS
SELECT 
    region,
    COUNT(*) as nombre_communes,
    ROUND(AVG(population)::numeric, 0) as population_moyenne,
    ROUND(AVG(densite)::numeric, 2) as densite_moyenne,
    ROUND(AVG(taux_urbanisation)::numeric, 3) as taux_urbanisation_moyen,
    ROUND(AVG(taux_alphabetisation)::numeric, 3) as taux_alphabetisation_moyen,
    ROUND(AVG(age_median)::numeric, 1) as age_median_moyen,
    ROUND(AVG(revenu_moyen_fcfa)::numeric, 0) as revenu_moyen_fcfa
FROM donnees_socioeconomiques
GROUP BY region
ORDER BY region;

-- Vue 4: Demandes par type de document
CREATE OR REPLACE VIEW v_demandes_par_document AS
SELECT 
    type_document,
    categorie_document,
    COUNT(*) as nombre_enregistrements,
    SUM(nombre_demandes) as total_demandes,
    ROUND(AVG(delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(taux_rejet)::numeric, 3) as taux_rejet_moyen
FROM demandes_services_public
GROUP BY type_document, categorie_document
ORDER BY total_demandes DESC;

-- Vue 5: Analyse temporelle des demandes
CREATE OR REPLACE VIEW v_demandes_temporel AS
SELECT 
    annee_demande,
    mois_demande,
    jour_semaine_demande,
    COUNT(*) as nombre_types_demandes,
    SUM(nombre_demandes) as total_demandes,
    ROUND(AVG(delai_traitement_jours)::numeric, 2) as delai_moyen,
    ROUND(AVG(taux_rejet)::numeric, 3) as taux_rejet_moyen
FROM demandes_services_public
GROUP BY annee_demande, mois_demande, jour_semaine_demande
ORDER BY annee_demande DESC, mois_demande DESC;

-- Afficher un message de confirmation
\echo 'Vues créées avec succès!';

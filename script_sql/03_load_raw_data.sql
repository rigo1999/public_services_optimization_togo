-- Script 3: Chargement des données RAW depuis CSV
-- =====================================================
\c service_public_db;

\echo '📥 Chargement des données CSV dans le schéma RAW...';

-- Importer les communes
\copy raw.communes (commune_id, commune, prefecture, region, latitude, longitude, altitude_m, superficie_km2, population_densite, code_postal, type_commune, distance_capitale_km, zone_climatique) FROM '02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/details_communes_cleaned.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

\echo '✅ Communes chargées';

-- Importer les centres de service
\copy raw.centres_service (centre_id, nom_centre, type_centre, region, prefecture, commune, quartier, latitude, longitude, personnel_capacite_jour, nombre_guichets, heures_ouverture, horaire_nuit, equipement_numerique, date_ouverture, statut_centre, annee_ouverture, mois_ouverture) FROM '02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/centres_service_cleaned.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

\echo '✅ Centres de service chargés';

-- Importer les demandes
\copy raw.demandes_services_public (demande_id, region, prefecture, commune, quartier, type_document, categorie_document, nombre_demandes, delai_traitement_jours, taux_rejet, date_demande, motif_demande, statut_demande, canal_demande, age_demandeur, sexe_demandeur, annee_demande, mois_demande, jour_semaine_demande) FROM '02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/demande_services_public_cleaned.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

\echo '✅ Demandes de services publics chargées';

-- Importer les données socio-économiques
\copy raw.donnees_socioeconomiques (region, prefecture, commune, population, superficie_km2, densite, taux_urbanisation, taux_alphabetisation, age_median, nombre_menages, revenu_moyen_fcfa) FROM '02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/donnees_socioeconomiques_cleaned.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

\echo '✅ Données socio-économiques chargées';

\echo '✅ Chargement RAW terminé!';
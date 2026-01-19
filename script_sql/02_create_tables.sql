-- Script 2: Création du schéma logique (RAW et DW)
-- =====================================================
-- Se connecter à service_public_db
\c service_public_db;

-- ========================================
-- CRÉATION DES SCHÉMAS
-- ========================================
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS dw;

\echo 'Schémas créés: raw et dw';

-- ========================================
-- DIMENSION CENTRALE: TERRITOIRE
-- ========================================
CREATE TABLE dw.dim_territoire (
    id_territoire SERIAL PRIMARY KEY,
    region TEXT NOT NULL,
    prefecture TEXT NOT NULL,
    commune TEXT NOT NULL,
    quartier TEXT,
    latitude DECIMAL(10, 4),
    longitude DECIMAL(10, 4),
    code_postal VARCHAR(20),
    CONSTRAINT uq_territoire UNIQUE (region, prefecture, commune, quartier)
);

CREATE INDEX idx_dim_territoire_region ON dw.dim_territoire(region);
CREATE INDEX idx_dim_territoire_commune ON dw.dim_territoire(commune);

\echo 'Dimension TERRITOIRE créée';

-- ========================================
-- TABLES RAW (chargement des CSV bruts)
-- ========================================

-- RAW: Communes
CREATE TABLE raw.communes (
    commune_id VARCHAR(50),
    commune VARCHAR(100),
    prefecture VARCHAR(100),
    region VARCHAR(100),
    latitude DECIMAL(10, 4),
    longitude DECIMAL(10, 4),
    altitude_m INT,
    superficie_km2 DECIMAL(10, 2),
    population_densite INT,
    code_postal VARCHAR(20),
    type_commune VARCHAR(50),
    distance_capitale_km INT,
    zone_climatique VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RAW: Centres de Service
CREATE TABLE raw.centres_service (
    centre_id VARCHAR(50),
    nom_centre VARCHAR(200),
    type_centre VARCHAR(100),
    region VARCHAR(100),
    prefecture VARCHAR(100),
    commune VARCHAR(100),
    quartier VARCHAR(100),
    latitude DECIMAL(10, 4),
    longitude DECIMAL(10, 4),
    personnel_capacite_jour INT,
    nombre_guichets INT,
    heures_ouverture VARCHAR(50),
    horaire_nuit VARCHAR(10),
    equipement_numerique VARCHAR(50),
    date_ouverture DATE,
    statut_centre VARCHAR(50),
    annee_ouverture INT,
    mois_ouverture INT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RAW: Demandes de Services Publics
CREATE TABLE raw.demandes_services_public (
    demande_id VARCHAR(50),
    region VARCHAR(100),
    prefecture VARCHAR(100),
    commune VARCHAR(100),
    quartier VARCHAR(100),
    type_document VARCHAR(100),
    categorie_document VARCHAR(100),
    nombre_demandes INT,
    delai_traitement_jours INT,
    taux_rejet DECIMAL(5, 2),
    date_demande DATE,
    motif_demande VARCHAR(100),
    statut_demande VARCHAR(50),
    canal_demande VARCHAR(100),
    age_demandeur INT,
    sexe_demandeur VARCHAR(10),
    annee_demande INT,
    mois_demande INT,
    jour_semaine_demande VARCHAR(20),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RAW: Données Socio-économiques
CREATE TABLE raw.donnees_socioeconomiques (
    region VARCHAR(100),
    prefecture VARCHAR(100),
    commune VARCHAR(100),
    population INT,
    superficie_km2 DECIMAL(10, 2),
    densite INT,
    taux_urbanisation DECIMAL(5, 3),
    taux_alphabetisation DECIMAL(5, 3),
    age_median INT,
    nombre_menages INT,
    revenu_moyen_fcfa DECIMAL(12, 2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

\echo 'Tables RAW créées';

-- ========================================
-- TABLES DW (modèle analytique)
-- ========================================

-- DW: Dimension Communes (enrichie)
CREATE TABLE dw.dim_communes (
    id_commune SERIAL PRIMARY KEY,
    id_territoire INT NOT NULL,
    commune_code VARCHAR(50),
    type_commune VARCHAR(50),
    altitude_m INT,
    superficie_km2 DECIMAL(10, 2),
    population_densite INT,
    distance_capitale_km INT,
    zone_climatique VARCHAR(50),
    FOREIGN KEY (id_territoire) REFERENCES dw.dim_territoire(id_territoire)
);

-- DW: Dimension Centres de Service
CREATE TABLE dw.dim_centres_service (
    id_centre SERIAL PRIMARY KEY,
    centre_code VARCHAR(50),
    id_territoire INT NOT NULL,
    nom_centre VARCHAR(200),
    type_centre VARCHAR(100),
    personnel_capacite_jour INT,
    nombre_guichets INT,
    heures_ouverture VARCHAR(50),
    horaire_nuit VARCHAR(10),
    equipement_numerique VARCHAR(50),
    date_ouverture DATE,
    statut_centre VARCHAR(50),
    FOREIGN KEY (id_territoire) REFERENCES dw.dim_territoire(id_territoire)
);

-- DW: Dimension Type de Document
CREATE TABLE dw.dim_type_document (
    id_type_document SERIAL PRIMARY KEY,
    type_document VARCHAR(100) NOT NULL,
    categorie_document VARCHAR(100),
    CONSTRAINT uq_type_document UNIQUE (type_document, categorie_document)
);

-- DW: Dimension Données Socio-économiques
CREATE TABLE dw.dim_socioeconomique (
    id_socio SERIAL PRIMARY KEY,
    id_territoire INT NOT NULL,
    population INT,
    densite INT,
    taux_urbanisation DECIMAL(5, 3),
    taux_alphabetisation DECIMAL(5, 3),
    age_median INT,
    nombre_menages INT,
    revenu_moyen_fcfa DECIMAL(12, 2),
    FOREIGN KEY (id_territoire) REFERENCES dw.dim_territoire(id_territoire)
);

-- DW: Table de Faits - Demandes
CREATE TABLE dw.fact_demandes (
    id_fact SERIAL PRIMARY KEY,
    id_territoire INT NOT NULL,
    id_type_document INT NOT NULL,
    demande_code VARCHAR(50),
    nombre_demandes INT,
    delai_traitement_jours INT,
    taux_rejet DECIMAL(5, 2),
    date_demande DATE,
    motif_demande VARCHAR(100),
    statut_demande VARCHAR(50),
    canal_demande VARCHAR(100),
    age_demandeur INT,
    sexe_demandeur VARCHAR(10),
    annee_demande INT,
    mois_demande INT,
    jour_semaine_demande VARCHAR(20),
    FOREIGN KEY (id_territoire) REFERENCES dw.dim_territoire(id_territoire),
    FOREIGN KEY (id_type_document) REFERENCES dw.dim_type_document(id_type_document)
);

\echo 'Tables DW créées';

-- ========================================
-- INDEX POUR LES PERFORMANCES
-- ========================================
CREATE INDEX idx_fact_demandes_territoire ON dw.fact_demandes(id_territoire);
CREATE INDEX idx_fact_demandes_date ON dw.fact_demandes(date_demande);
CREATE INDEX idx_fact_demandes_type ON dw.fact_demandes(id_type_document);
CREATE INDEX idx_dim_centres_territoire ON dw.dim_centres_service(id_territoire);
CREATE INDEX idx_dim_communes_territoire ON dw.dim_communes(id_territoire);

\echo 'Index créés pour les performances';

-- ========================================
-- CONFIRMATION
-- ========================================
\echo '✅ Architecture Data Warehouse créée avec succès!';

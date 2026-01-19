-- Dimensions pour tous les datasets

-- 1. DIM_DEMANDE (from demande_services_public_cleaned.csv)
DROP TABLE IF EXISTS dw.dim_demande CASCADE;
CREATE TABLE dw.dim_demande (
    demande_id TEXT PRIMARY KEY,
    region TEXT,
    prefecture TEXT,
    commune TEXT,
    quartier TEXT,
    type_document TEXT,
    categorie_document TEXT,
    nombre_demandes INT,
    delai_traitement_jours INT,
    taux_rejet FLOAT,
    date_demande DATE,
    motif_demande TEXT,
    statut_demande TEXT,
    canal_demande TEXT,
    age_demandeur INT,
    sexe_demandeur TEXT,
    annee_demande INT,
    mois_demande INT,
    jour_semaine_demande TEXT,
    id_territoire INT REFERENCES dw.dim_territoire(territoire_id)
);
CREATE INDEX idx_dim_demande_territoire ON dw.dim_demande(id_territoire);

-- 2. DIM_DOCUMENT (from document_administratif_cleaned.csv)
DROP TABLE IF EXISTS dw.dim_document CASCADE;
CREATE TABLE dw.dim_document (
    document_id SERIAL PRIMARY KEY,
    annee INT,
    mois INT,
    region TEXT,
    prefecture TEXT,
    commune TEXT,
    type_document TEXT,
    nombre_demandes INT,
    delai_moyen_jours INT,
    taux_rejet_moyen FLOAT,
    periode TEXT,
    id_territoire INT REFERENCES dw.dim_territoire(territoire_id)
);
CREATE INDEX idx_dim_document_territoire ON dw.dim_document(id_territoire);

-- 3. DIM_SOCIOECONOMIQUE (from donnees_socioeconomiques_cleaned.csv)
DROP TABLE IF EXISTS dw.dim_socioeconomique CASCADE;
CREATE TABLE dw.dim_socioeconomique (
    socioeco_id SERIAL PRIMARY KEY,
    region TEXT,
    prefecture TEXT,
    commune TEXT,
    population INT,
    superficie_km2 FLOAT,
    densite FLOAT,
    taux_urbanisation FLOAT,
    taux_alphabetisation FLOAT,
    age_median INT,
    nombre_menages INT,
    id_territoire INT REFERENCES dw.dim_territoire(territoire_id)
);
CREATE INDEX idx_dim_socioeconomique_territoire ON dw.dim_socioeconomique(id_territoire);

-- 4. DIM_COMMUNE (from details_communes_cleaned.csv)
DROP TABLE IF EXISTS dw.dim_commune CASCADE;
CREATE TABLE dw.dim_commune (
    commune_id SERIAL PRIMARY KEY,
    region TEXT,
    prefecture TEXT,
    commune TEXT,
    id_territoire INT REFERENCES dw.dim_territoire(territoire_id)
);
CREATE INDEX idx_dim_commune_territoire ON dw.dim_commune(id_territoire);

-- 5. DIM_DEVELOPPEMENT (from developpement_cleaned.csv)
DROP TABLE IF EXISTS dw.dim_developpement CASCADE;
CREATE TABLE dw.dim_developpement (
    dev_id SERIAL PRIMARY KEY,
    region TEXT,
    prefecture TEXT,
    commune TEXT,
    id_territoire INT REFERENCES dw.dim_territoire(territoire_id)
);
CREATE INDEX idx_dim_developpement_territoire ON dw.dim_developpement(id_territoire);

-- 6. DIM_LOGS (from logs_activite_cleaned.csv)
DROP TABLE IF EXISTS dw.dim_logs CASCADE;
CREATE TABLE dw.dim_logs (
    log_id SERIAL PRIMARY KEY,
    date_log DATE,
    type_activite TEXT
);

-- 7. DIM_RESEAU (from reseau_routier_togo_ext_cleaned.csv)
DROP TABLE IF EXISTS dw.dim_reseau CASCADE;
CREATE TABLE dw.dim_reseau (
    reseau_id SERIAL PRIMARY KEY,
    region TEXT,
    prefecture TEXT,
    commune TEXT,
    id_territoire INT REFERENCES dw.dim_territoire(territoire_id)
);
CREATE INDEX idx_dim_reseau_territoire ON dw.dim_reseau(id_territoire);

DROP TABLE IF EXISTS dw.dim_centre CASCADE;

CREATE TABLE dw.dim_centre (
    centre_id TEXT PRIMARY KEY,
    nom_centre TEXT,
    type_centre TEXT,
    region TEXT,
    prefecture TEXT,
    commune TEXT,
    quartier TEXT,
    latitude FLOAT,
    longitude FLOAT,
    personnel_capacite_jour INT,
    nombre_guichets INT,
    heures_ouverture TEXT,
    horaire_nuit TEXT,
    equipement_numerique TEXT,
    date_ouverture DATE,
    statut_centre TEXT,
    annee_ouverture INT,
    mois_ouverture INT,
    id_territoire INT REFERENCES dw.dim_territoire(territoire_id)
);

CREATE INDEX idx_dim_centre_territoire ON dw.dim_centre(id_territoire);



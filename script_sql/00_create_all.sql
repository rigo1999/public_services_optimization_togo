-- Script 0: Orchestration complète (exécuter une seule fois)
-- =====================================================
-- Ce script exécute tous les étapes de la création de la base de données

\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
\echo 'CRÉATION DE LA BASE DE DONNÉES SERVICE PUBLIC DB';
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';

-- ÉTAPE 1: Création de la base
\echo '';
\echo 'ÉTAPE 1: Création de la base de données...';
CREATE DATABASE IF NOT EXISTS service_public_db;
\echo ' Base de données créée';

-- Se connecter à la base
\c service_public_db;

-- ÉTAPE 2: Création du schéma logique
\echo '';
\echo ' ÉTAPE 2: Création des schémas (RAW et DW)...';
CREATE SCHEMA IF NOT EXISTS dw;
\echo ' Schémas créés';

-- ÉTAPE 3: Création des tables
\echo ' ÉTAPE 3: Création de la Dimension TERRITOIRE (clé centrale)...';

CREATE TABLE IF NOT EXISTS dw.dim_territoire (
   id_territoire SERIAL PRIMARY KEY,
    region TEXT NOT NULL,
    prefecture TEXT NOT NULL,
    commune TEXT NOT NULL,
    CONSTRAINT uq_territoire UNIQUE (region, prefecture, commune)
);

CREATE INDEX IF NOT EXISTS idx_dim_territoire_region ON dw.dim_territoire(region);
CREATE INDEX IF NOT EXISTS idx_dim_territoire_commune ON dw.dim_territoire(commune);
CREATE INDEX IF NOT EXISTS idx_dim_territoire_prefecture ON dw.dim_territoire(prefecture);

\echo ' Dimension TERRITOIRE créée';
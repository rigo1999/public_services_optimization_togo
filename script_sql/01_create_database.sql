-- Script 1: Création de la base de données
-- =====================================================
-- Crée la base de données service_public_db

-- Vérifier si la base existe et la supprimer si nécessaire
DROP DATABASE IF EXISTS service_public_db;

-- Créer la base de données
CREATE DATABASE service_public_db
    WITH
    ENCODING 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE = template0;

-- Afficher un message de confirmation
\echo 'Base de données service_public_db créée avec succès!'

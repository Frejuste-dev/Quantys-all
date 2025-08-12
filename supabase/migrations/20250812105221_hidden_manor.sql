-- Script d'initialisation MySQL pour Sage X3
-- Ce script sera exécuté automatiquement lors du premier démarrage du conteneur MySQL

-- Création de la base de données avec le bon charset
CREATE DATABASE IF NOT EXISTS sage_x3_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Utilisation de la base de données
USE sage_x3_db;

-- Configuration des paramètres MySQL pour optimiser les performances
SET GLOBAL innodb_buffer_pool_size = 268435456; -- 256MB
SET GLOBAL max_connections = 200;
SET GLOBAL innodb_log_file_size = 67108864; -- 64MB

-- Création d'un utilisateur avec les privilèges nécessaires (si pas déjà fait par les variables d'environnement)
-- CREATE USER IF NOT EXISTS 'sage_x3_user'@'%' IDENTIFIED BY 'sage_x3_password';
-- GRANT ALL PRIVILEGES ON sage_x3_db.* TO 'sage_x3_user'@'%';
-- FLUSH PRIVILEGES;

-- Les tables seront créées automatiquement par SQLAlchemy
-- Mais on peut ajouter des configurations spécifiques si nécessaire

-- Configuration pour les sessions longues
SET GLOBAL wait_timeout = 28800;
SET GLOBAL interactive_timeout = 28800;
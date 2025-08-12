#!/usr/bin/env python3
"""
Script de configuration initiale MySQL
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import db_manager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_mysql():
    """Configure la base de données MySQL"""
    
    # Charger les variables d'environnement
    load_dotenv()
    
    logger.info("Configuration de la base de données MySQL")
    
    try:
        # Test de connexion
        if not db_manager.health_check():
            raise Exception("Impossible de se connecter à MySQL")
        
        logger.info("Connexion MySQL OK")
        
        # Créer les tables
        db_manager.create_tables()
        logger.info("Tables créées avec succès")
        
        # Vérifier les tables
        session = db_manager.get_session()
        try:
            # Test simple
            session.execute("SELECT 1")
            logger.info("Base de données prête à l'utilisation")
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Erreur lors de la configuration: {e}")
        raise

if __name__ == "__main__":
    setup_mysql()
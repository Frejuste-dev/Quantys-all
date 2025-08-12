#!/usr/bin/env python3
"""
Script de migration des données de SQLite vers MySQL
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime
from dotenv import load_dotenv

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import db_manager
from models.session import Session
from models.inventory_item import InventoryItem

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_sqlite_to_mysql():
    """Migre les données de SQLite vers MySQL"""
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Chemin vers l'ancienne base SQLite
    sqlite_path = 'database/sage_x3.db'
    
    if not os.path.exists(sqlite_path):
        logger.info("Aucune base SQLite trouvée, rien à migrer")
        return
    
    logger.info("Début de la migration SQLite -> MySQL")
    
    try:
        # Connexion à SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        
        # Créer les tables MySQL
        db_manager.create_tables()
        logger.info("Tables MySQL créées")
        
        # Migrer les sessions
        migrate_sessions(sqlite_conn)
        
        # Migrer les items d'inventaire
        migrate_inventory_items(sqlite_conn)
        
        sqlite_conn.close()
        logger.info("Migration terminée avec succès")
        
        # Optionnel: sauvegarder l'ancienne base
        backup_path = f"database/sage_x3_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.rename(sqlite_path, backup_path)
        logger.info(f"Ancienne base sauvegardée: {backup_path}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        raise

def migrate_sessions(sqlite_conn):
    """Migre les sessions"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM sessions")
    
    mysql_session = db_manager.get_session()
    
    try:
        count = 0
        for row in cursor.fetchall():
            session = Session(
                id=row['id'],
                original_filename=row['original_filename'],
                original_file_path=row['original_file_path'],
                template_file_path=row['template_file_path'],
                completed_file_path=row['completed_file_path'],
                final_file_path=row['final_file_path'],
                status=row['status'],
                inventory_date=datetime.fromisoformat(row['inventory_date']) if row['inventory_date'] else None,
                nb_articles=row['nb_articles'] or 0,
                nb_lots=row['nb_lots'] or 0,
                total_quantity=row['total_quantity'] or 0.0,
                total_discrepancy=row['total_discrepancy'] or 0.0,
                adjusted_items_count=row['adjusted_items_count'] or 0,
                strategy_used=row['strategy_used'] or 'FIFO',
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.utcnow(),
                last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else datetime.utcnow(),
                header_lines=row['header_lines']
            )
            mysql_session.add(session)
            count += 1
        
        mysql_session.commit()
        logger.info(f"{count} sessions migrées")
        
    except Exception as e:
        mysql_session.rollback()
        logger.error(f"Erreur migration sessions: {e}")
        raise
    finally:
        mysql_session.close()

def migrate_inventory_items(sqlite_conn):
    """Migre les items d'inventaire"""
    cursor = sqlite_conn.cursor()
    
    # Vérifier si la table existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_items'")
    if not cursor.fetchone():
        logger.info("Table inventory_items non trouvée dans SQLite, skip")
        return
    
    cursor.execute("SELECT * FROM inventory_items")
    
    mysql_session = db_manager.get_session()
    
    try:
        count = 0
        for row in cursor.fetchall():
            item = InventoryItem(
                id=row['id'],
                session_id=row['session_id'],
                type_ligne=row['type_ligne'],
                numero_session=row['numero_session'],
                numero_inventaire=row['numero_inventaire'],
                rang=row['rang'],
                site=row['site'],
                quantite=row['quantite'],
                quantite_reelle_input=row['quantite_reelle_input'] or 0,
                indicateur_compte=row['indicateur_compte'],
                code_article=row['code_article'],
                emplacement=row['emplacement'],
                statut=row['statut'],
                unite=row['unite'],
                valeur=row['valeur'],
                zone_pk=row['zone_pk'],
                numero_lot=row['numero_lot'],
                date_lot=datetime.fromisoformat(row['date_lot']) if row['date_lot'] else None,
                quantite_corrigee=row['quantite_corrigee'],
                original_s_line_raw=row['original_s_line_raw'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow()
            )
            mysql_session.add(item)
            count += 1
        
        mysql_session.commit()
        logger.info(f"{count} items d'inventaire migrés")
        
    except Exception as e:
        mysql_session.rollback()
        logger.error(f"Erreur migration inventory_items: {e}")
        raise
    finally:
        mysql_session.close()

if __name__ == "__main__":
    migrate_sqlite_to_mysql()
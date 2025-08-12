import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.session import Base
import logging
import urllib.parse

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url=None):
        if database_url:
            self.database_url = database_url
        else:
            # Construction automatique de l'URL MySQL depuis les variables d'environnement
            mysql_host = os.getenv('MYSQL_HOST', 'localhost')
            mysql_port = os.getenv('MYSQL_PORT', '3306')
            mysql_user = os.getenv('MYSQL_USER', 'sage_x3_user')
            mysql_password = os.getenv('MYSQL_PASSWORD', '')
            mysql_database = os.getenv('MYSQL_DATABASE', 'sage_x3_db')
            
            # Échapper le mot de passe pour l'URL
            escaped_password = urllib.parse.quote_plus(mysql_password)
            
            self.database_url = f"mysql+pymysql://{mysql_user}:{escaped_password}@{mysql_host}:{mysql_port}/{mysql_database}?charset=utf8mb4"
        
        logger.info(f"Configuration base de données: {self.database_url.split('@')[0]}@***")
        
        self.engine = create_engine(
            self.database_url,
            echo=False,  # Mettre à True pour debug SQL
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            # Configuration spécifique MySQL
            connect_args={
                "charset": "utf8mb4",
                "autocommit": False
            } if self.database_url.startswith('mysql') else {}
        )
        
        self.SessionLocal = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False  # Évite que les objets deviennent détachés après commit
        ))
        
        self.create_tables()
    
    def create_tables(self):
        """Crée toutes les tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tables créées avec succès")
        except Exception as e:
            logger.error(f"Erreur création tables: {e}")
            raise
    
    def get_session(self):
        """Retourne une session de base de données"""
        return self.SessionLocal()
    
    def close_session(self):
        """Ferme la session"""
        self.SessionLocal.remove()
    
    def health_check(self):
        """Vérifie la santé de la base de données"""
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            logger.error(f"Health check DB failed: {e}")
            return False

# Instance globale
db_manager = DatabaseManager()
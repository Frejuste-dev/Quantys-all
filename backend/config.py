import os
from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Config:
    """Configuration centralisée de l'application"""
    
    # Dossiers
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', 'uploads')
    PROCESSED_FOLDER: str = os.getenv('PROCESSED_FOLDER', 'processed')
    FINAL_FOLDER: str = os.getenv('FINAL_FOLDER', 'final')
    ARCHIVE_FOLDER: str = os.getenv('ARCHIVE_FOLDER', 'archive')
    LOG_FOLDER: str = os.getenv('LOG_FOLDER', 'logs')
    
    # Limites
    MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB
    MAX_SESSIONS: int = int(os.getenv('MAX_SESSIONS', 100))
    SESSION_TIMEOUT: int = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 heure
    
    # Sécurité
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    ALLOWED_EXTENSIONS: set = field(default_factory=lambda: {'.csv', '.xlsx', '.xls'})
    
    # Configuration Sage X3 (externalisée)
    SAGE_COLUMNS: Dict[str, int] = {
        'TYPE_LIGNE': 0,
        'NUMERO_SESSION': 1,
        'NUMERO_INVENTAIRE': 2,
        'RANG': 3,
        'SITE': 4,
        'QUANTITE': 5,
        'QUANTITE_REELLE_IN_INPUT': 6,
        'INDICATEUR_COMPTE': 7,
        'CODE_ARTICLE': 8,
        'EMPLACEMENT': 9,
        'STATUT': 10,
        'UNITE': 11,
        'VALEUR': 12,
        'ZONE_PK': 13,
        'NUMERO_LOT': 14,
    })
    
    def __post_init__(self):
        """Création automatique des dossiers"""
        for folder in [self.UPLOAD_FOLDER, self.PROCESSED_FOLDER, 
                      self.FINAL_FOLDER, self.ARCHIVE_FOLDER, self.LOG_FOLDER]:
            os.makedirs(folder, exist_ok=True)

# Instance globale
config = Config()
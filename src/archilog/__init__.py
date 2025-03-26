import logging
import os
from dataclasses import dataclass




# Configurer le logging
logging.basicConfig(
    level=logging.INFO,  # On affiche au minimum les messages INFO
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("activity.log"),  # Enregistre dans un fichier
        logging.StreamHandler()  # Affiche dans la console
    ]
)

@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool

# Charger la configuration depuis les variables d'environnement
database_url = os.getenv("ARCHILOG_DATABASE_URL")
if not database_url:
    raise ValueError("La variable d'environnement 'ARCHILOG_DATABASE_URL' n'est pas définie")

debug = os.getenv("ARCHILOG_DEBUG", "False") == "True"

config = Config(
    DATABASE_URL=database_url,
    DEBUG=debug
)

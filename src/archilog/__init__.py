import os
from dataclasses import dataclass

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

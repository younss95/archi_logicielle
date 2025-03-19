from flask import Flask

from archilog.views.web import web_ui
from archilog import config

def create_app():
    app = Flask(__name__)

    # Charger la configuration depuis l'objet config
    app.config.from_object(config)

    app.secret_key = "test"  # Garde cette clé dans un fichier .env si possible

    # Enregistrer les Blueprints
    app.register_blueprint(web_ui)


    return app

from flask import Flask

from archilog.views.web import web_ui
from archilog import config

def create_app():
    app = Flask(__name__)

    # Charger la configuration depuis l'objet config
    app.config.from_prefixed_env(prefix="ARCHILOG_FLASK")


    # Enregistrer les Blueprints
    app.register_blueprint(web_ui)


    return app


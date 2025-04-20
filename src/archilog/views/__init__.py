from flask import Flask

from archilog.views.web import web_ui
from archilog.views.api import api_ui, spec


def create_app():
    app = Flask(__name__)

    # Charger la configuration depuis l'objet config
    app.config.from_prefixed_env(prefix="ARCHILOG_FLASK")


    # Enregistrer les Blueprints
    app.register_blueprint(web_ui)
    app.register_blueprint(api_ui)

    # Ajout de Spectree
    spec.register(app)


    return app


from flask import Flask
from archilog.views.web import web_ui


def create_app():
    app = Flask(__name__)
    app.secret_key = "test"

    # Enregistrer les Blueprints
    app.register_blueprint(web_ui)

    return app

from flask import Flask

import settings
import flask_cors
from web.controllers import api


def create_app():
    app = Flask(__name__)

    _configure_settings(app)
    _configure_cors(app)
    _configure_controllers(app)
    return app


def _configure_settings(app):
    app.config.from_object(settings)
    return app


def _configure_cors(app):
    flask_cors.CORS(app)
    return app


def _configure_controllers(app):
    app.register_blueprint(api)
    return app

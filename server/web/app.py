"""Configures a Flask app, readying it for execution"""
from flask import Flask


def create_app():
    app = Flask(__name__)

    _configure_settings(app)
    _configure_cors(app)
    _configure_controllers(app)
    _configure_response(app)
    return app


def _configure_settings(app):
    import settings
    app.config.from_object(settings)
    return app


def _configure_cors(app):
    import flask_cors
    flask_cors.CORS(app)
    return app


def _configure_controllers(app):
    from web.controllers import api
    app.register_blueprint(api)
    return app


def _configure_response(app):
    @app.after_request
    def after_request(resp):
        resp.headers['Content-Type'] = 'application/json'
        return resp

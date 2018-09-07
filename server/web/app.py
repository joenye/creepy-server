"""Configures a Flask app, readying it for execution"""
import logging

from flask import Flask
from flask_socketio import SocketIO


logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    _configure_settings(app)
    _configure_cors(app)

    _configure_http_handlers(app)
    _configure_http_error_handlers(app)
    _configure_http_response(app)

    socketio = SocketIO(app)
    _configure_socket_handlers(socketio)

    return lambda *args, **kwargs: socketio.run(app, *args, **kwargs)


def _configure_settings(app):
    import settings
    app.config.from_object(settings)
    return app


def _configure_cors(app):
    import flask_cors
    flask_cors.CORS(app)
    return app


def _configure_http_handlers(app):
    from web.http.handlers import http_api
    app.register_blueprint(http_api)
    return app


def _configure_http_error_handlers(app):
    from web.http import error_handler
    error_handler.init_api(app)
    return app


def _configure_http_response(app):
    @app.after_request
    def after_request(resp):
        resp.headers['Content-Type'] = 'application/json'
        resp.headers['Creepy'] = 'Cave'
        return resp


def _configure_socket_handlers(socketio: SocketIO):
    from web.socket.handlers import configure_handlers
    configure_handlers(socketio)
    return socketio

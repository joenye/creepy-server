"""Configure Flask app, readying it for execution"""
import logging

from flask import Flask
from flask_socketio import SocketIO


LOGGER = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    _configure_settings(app)

    _configure_http_handlers(app)
    _configure_http_error_handlers(app)
    _configure_http_response(app)

    socketio = SocketIO(app, engineio_logger=True, cors_allowed_origins=[])
    _configure_socket_handlers(socketio)

    return lambda *args, **kwargs: socketio.run(app, *args, **kwargs)


def _configure_settings(app):
    from common import settings

    app.config.from_object(settings)
    return app


def _configure_http_handlers(app):
    from web.http.handlers import HTTP_API

    app.register_blueprint(HTTP_API)
    return app


def _configure_http_error_handlers(app):
    from web.http import error_handler

    error_handler.init_api(app)
    return app


def _configure_http_response(app):
    @app.after_request
    def _after_request(resp):
        resp.headers["Content-Type"] = "application/json"
        return resp


def _configure_socket_handlers(socketio: SocketIO):
    from web.socket.handlers import configure_handlers

    configure_handlers(socketio)
    return socketio

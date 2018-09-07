"""Executes a Flask app"""
import settings
from web import app


if __name__ == '__main__':
    host = settings.FLASK_HOST
    port = settings.FLASK_PORT
    debug = settings.FLASK_DEBUG

    app.create_app()(host=host, port=port, debug=debug)

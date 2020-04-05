"""Executes a Flask app"""
from web import app
from common import settings

settings.configure_logger()


if __name__ == "__main__":
    HOST = settings.FLASK_HOST
    PORT = settings.FLASK_PORT
    DEBUG = settings.FLASK_DEBUG

    app.create_app()(host=HOST, port=PORT, debug=DEBUG)

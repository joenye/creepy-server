"""Executes a Flask app"""
import web
import settings


_app = web.create_app()

if __name__ == '__main__':
    host = settings.FLASK_HOST
    port = settings.FLASK_PORT
    debug = settings.FLASK_DEBUG
    _app.run(host=host, port=port, debug=debug)

import web
import settings


app = web.create_app()

if __name__ == '__main__':
    host = settings.FLASK_HOST
    port = settings.FLASK_PORT
    debug = settings.FLASK_DEBUG
    app.run(host=host, port=port, debug=debug)

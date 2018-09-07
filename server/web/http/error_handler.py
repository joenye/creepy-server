"""Configures error handling"""
import logging

from web.http import errors, marshal


logger = logging.getLogger(__name__)


def handle_api_error(e):
    status = e.status
    code = e.code
    message = e.message

    data = e.enrich_response_data({
        'status': status,
        'code': code,
        'message': message,
    })

    return marshal.marshal(data), status


def handle_unexpected_error(api, e):
    status = errors.ApiException.status
    code = errors.ApiException.code
    message = errors.ApiException.message

    data = {
        'status': status,
        'code': code,
        'message': message,
    }

    logger.exception(e)

    return marshal.marshal(data), status


def init_api(app):
    @app.errorhandler(errors.ApiException)
    def api_error_handler(e):
        return handle_api_error(e)

    @app.errorhandler(Exception)
    def unexpected_error_handler(e):
        return handle_unexpected_error(app, e)

    return app

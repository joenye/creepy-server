"""Configures error handling"""
import logging

from web import marshal
from web.http import errors


LOGGER = logging.getLogger(__name__)


def handle_api_error(err):
    status = err.status
    code = err.code
    message = err.message

    data = err.enrich_response_data(
        {"status": status, "code": code, "message": message}
    )

    return marshal.marshal(data), status


def handle_unexpected_error(err):
    status = errors.ApiException.status
    code = errors.ApiException.code
    message = errors.ApiException.message

    data = {
        "status": status,
        "code": code,
        "message": message,
    }

    LOGGER.exception(err)

    return marshal.marshal(data), status


def init_api(app):
    @app.errorhandler(errors.ApiException)
    def _api_error_handler(err):
        return handle_api_error(err)

    @app.errorhandler(Exception)
    def _unexpected_error_handler(err):
        return handle_unexpected_error(err)

    return app

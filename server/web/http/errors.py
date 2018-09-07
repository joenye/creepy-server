"""Centralises definitions of API errors"""


class ApiErrorCode:
    SERVER_ERROR = 'server_error'
    PARSE_ERROR = 'parse_error'
    VALIDATION_ERROR = 'validation_error'
    INVALID_TOKEN = 'invalid_token'
    FORBIDDEN = 'forbidden'
    NOT_FOUND = 'not_found'
    METHOD_NOT_ALLOWED = 'method_not_allowed'


class ApiException(Exception):
    status = 500
    code = ApiErrorCode.SERVER_ERROR
    message = "Something went horribly wrong."

    def __init__(self, code=None, message=None):
        if code:
            self.code = code
        if message:
            self.message = message

    def enrich_response_data(self, data):
        return data


class ApiParseError(ApiException):
    status = 400
    code = ApiErrorCode.PARSE_ERROR
    message = 'I only understand JSON, sorry.'


class ApiValidationError(ApiException):
    status = 400
    code = ApiErrorCode.VALIDATION_ERROR
    message = "A validation error has occured."
    errors = None

    def __init__(self, errors=None, **kwargs):
        self.errors = errors
        super(ApiValidationError, self).__init__(**kwargs)

    def enrich_response_data(self, data):
        if self.errors:
            data['errors'] = self.errors
        return data


class ApiInvalidToken(ApiException):
    status = 401
    code = ApiErrorCode.INVALID_TOKEN
    message = 'Invalid or expired token.'


class ApiForbidden(ApiException):
    status = 403
    code = ApiErrorCode.FORBIDDEN
    message = "You can't do that."


class ApiNotFound(ApiException):
    status = 404
    code = ApiErrorCode.NOT_FOUND
    message = "This is not the cave you're looking for."

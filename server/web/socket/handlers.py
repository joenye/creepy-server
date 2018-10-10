"""Configures websocket event handlers"""
import logging

from marshmallow.validate import OneOf
from marshmallow import fields, Schema, ValidationError
from flask_socketio import SocketIO, emit

from common.point import Point
from web import marshal
from game import dm, errors
from game.constants import Action


logger = logging.getLogger(__name__)


class PositionSchema(Schema):
    x = fields.Integer(required=True)
    y = fields.Integer(required=True)
    z = fields.Integer(required=True)


class ActionSchema(Schema):
    name = fields.String(required=True, validate=OneOf(Action.values()))


class ActionNavigateSchema(ActionSchema):
    target_pos = fields.Nested(PositionSchema, required=True)


class JsonSchema(Schema):
    action = fields.Nested(ActionSchema, required=True)


def configure_handlers(socketio: SocketIO):
    @socketio.on('connect')
    def handle_connect():
        logger.info('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info('Client disconnected')

    @socketio.on('message')
    def handle_message(message):
        logger.info('Received plain message: ' + str(message))

    @socketio.on('json')
    def handle_json(payload):
        logger.info('Received json message: ' + str(payload))

        try:
            target_pos = Point(**payload['action']['target_pos'])
        except IndexError:
            target_pos = None

        try:
            action_name = JsonSchema().load(payload)['action']['name']
        except ValidationError as err:
            return _emit_response(
                status='ERROR_INVALID_INPUT',
                message={
                    'errors': err.messages,
                    'target_pos': target_pos,
                }
            )

        if action_name == Action.NAVIGATE.value:
            _handle_navigate(payload, target_pos)

    def _handle_navigate(payload: dict, target_pos: Point):
        try:
            ActionNavigateSchema().load(payload['action'])
        except ValidationError as err:
            return _emit_response(
                status='ERROR_INVALID_INPUT',
                message={
                    'errors': err.messages,
                    'target_pos': target_pos,
                }
            )

        try:
            tile = dm.navigate(target_pos)
        except errors.InvalidAction as err:
            return _emit_response(
                status='NAVIGATE_ERROR',
                message={
                    'errors': [str(err)],
                    'target_pos': target_pos,
                }
            )

        return _emit_response(
            status='NAVIGATE_SUCCESS',
            message={
                'new_pos': target_pos,
                'background': tile['background'],
            }
        )


def _marshal_response(message: dict):
    class ResponseSerializer(Schema):
        background = fields.String()
        errors = fields.List(fields.String())
        new_pos = fields.Nested(PositionSchema)
        target_pos = fields.Nested(PositionSchema)

    return marshal.marshal(message, schema=ResponseSerializer())


def _emit_response(status: str, message: dict):
    emit('json', {'status': status, 'message': _marshal_response(message)}, broadcast=True)

"""Configure websocket event handlers"""
import logging

from marshmallow.validate import OneOf
from marshmallow import fields, Schema, ValidationError, INCLUDE
from flask_socketio import SocketIO, emit

from common.point import Point
from common.enum import ClientAction, EntityType, Direction
from web import marshal
from game import actions, errors


logger = logging.getLogger(__name__)


class PositionSchema(Schema):
    x = fields.Integer(required=True)
    y = fields.Integer(required=True)
    z = fields.Integer(required=True)


class EntitySchema(Schema):
    pos = fields.Nested(PositionSchema, required=True)


class TileSchema(Schema):
    background = fields.String(required=True)
    pos = fields.Nested(PositionSchema, attribute='position')
    exits_pos = fields.Dict(
        keys=fields.String(validate=OneOf(Direction.values())),
        values=fields.Nested(PositionSchema, required=True),
    )
    entities = fields.Dict(
        keys=fields.String(validate=OneOf(EntityType.values())),
        values=fields.Nested(EntitySchema, required=True)
    )


class ClientActionSchema(Schema):
    class Meta:
        unknown = INCLUDE

    name = fields.String(required=True, validate=OneOf(ClientAction.values()))


class ActionNavigateSchema(ClientActionSchema):
    target_pos = fields.Nested(PositionSchema, required=True)


class JsonSchema(Schema):
    action = fields.Nested(ClientActionSchema, required=True)


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
        except KeyError:
            target_pos = None

        try:
            action_name = JsonSchema().load(payload)['action']['name'].lower()
        except ValidationError as err:
            return _emit_response(
                status='ERROR_INVALID_INPUT',
                message={
                    'errors': err.messages,
                    'target_pos': target_pos,
                }
            )

        if action_name == ClientAction.NAVIGATE.value:
            return _handle_navigate(payload, target_pos)
        if action_name == ClientAction.REFRESH_ALL.value:
            return _handle_refresh_all(payload)

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
            tile = actions.navigate(target_pos)
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
                'new_tile': tile,
            }
        )

    def _handle_refresh_all(payload: dict):
        current_pos = actions.get_or_update_current_position()
        all_tiles = actions.get_all_visited_tiles()

        return _emit_response(
            status='REFRESH_ALL_SUCCESS',
            message={
                'current_pos': current_pos,
                'all_tiles': all_tiles,
            }
        )


def _emit_response(status: str, message: dict):
    emit('json', {'status': status, 'message': _marshal_response(message)}, broadcast=True)


def _marshal_response(message: dict):
    class ResponseSerializer(Schema):
        new_tile = fields.Nested(TileSchema)
        errors = fields.List(fields.String())
        new_pos = fields.Nested(PositionSchema)
        current_pos = fields.Nested(PositionSchema)
        target_pos = fields.Nested(PositionSchema)
        all_tiles = fields.Dict(
            keys=fields.Integer(),  # Floor
            values=fields.Nested(TileSchema, many=True)  # List of tiles
        )

    return marshal.marshal(message, schema=ResponseSerializer())

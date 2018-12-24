"""Configures HTTP routes"""
import logging

import flask
from marshmallow import fields, Schema

from web import marshal
from game import builder, actions

logger = logging.getLogger(__name__)

http_api = flask.Blueprint('http_api', __name__)


class PositionSchema(Schema):
    x = fields.Integer()
    y = fields.Integer()
    z = fields.Integer()


class NavigateSchema(Schema):
    background = fields.String()
    current_position = fields.Nested(PositionSchema)
    available_actions = fields.String(many=True)


@http_api.route('/current')
def current():
    current_pos = actions.get_or_update_current_position()

    tile = builder.get_or_create_tile(current_pos)
    background = tile['background']

    # Build response
    resp = {
        'background': background,
        'current_position': current_pos,
        'available_actions': actions.get_available_actions(),
    }
    return marshal.marshal(resp, schema=NavigateSchema()), 200

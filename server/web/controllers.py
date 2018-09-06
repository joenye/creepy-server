"""Configures routes"""
import flask
import logging
from marshmallow import fields, Schema

import database
from game import dm
from web import errors, marshal
from tiles import builder, cavern, tunnel
from common.direction import Direction

logger = logging.getLogger(__name__)

api = flask.Blueprint('api', __name__)


#######################################################################
#                             Marshalling                             #
#######################################################################

class PositionSchema(Schema):
    x = fields.Integer()
    y = fields.Integer()
    z = fields.Integer()


class NavigateSchema(Schema):
    background = fields.String()
    current_position = fields.Nested(PositionSchema)
    available_actions = fields.String(many=True)


#######################################################################
#                               Routes                                #
#######################################################################


@api.route('/current')
def current():
    current_pos = dm.get_or_update_current_position()

    tile = builder.get_or_create_tile(current_pos)
    background = tile['background']

    # Build response
    resp = {
        'background': background,
        'current_position': current_pos,
        'available_actions': dm.get_available_actions(),
    }
    return marshal.marshal(resp, schema=NavigateSchema()), 200


@api.route('/navigate')
def navigate():
    direction_str = flask.request.args.get('direction')
    direction = Direction.from_string(direction_str)

    current_pos = dm.get_or_update_current_position()
    target_pos = current_pos.translate(direction)

    # TODO: Store available actions in db and validate the intended action
    # is inside the list of available actions
    current_tile = database.get_tile(current_pos)
    if current_tile['sides'][direction.value]['is_blocked']:
        raise errors.ApiForbidden

    # Fetch tile and update position
    tile = builder.get_or_create_tile(target_pos)
    database.update_current_position(target_pos)

    # Build response
    resp = {
        'background': tile['background'],
        'current_position': target_pos,
        'available_actions': dm.get_available_actions(),
    }
    return marshal.marshal(resp, schema=NavigateSchema()), 200


#######################################################################
#                         Development routes                          #
#######################################################################


@api.route('/debug/cavern')
def get_cavern():
    file_dir, filename = cavern.render_tile()
    return flask.send_from_directory(file_dir, filename)


@api.route('/debug/tunnel')
def get_tunnel():
    try:
        file_dir, filename = tunnel.render_tile()
    # TODO: Fix tile-gen bug so no need for this (potentially infinite) check
    except ValueError:
        return get_tunnel()

    return flask.send_from_directory(file_dir, filename)

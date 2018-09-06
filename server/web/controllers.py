import json
import flask
import logging
import marshmallow

import database
from game import actions
from tiles import builder, cavern, tunnel
from common.direction import Direction

logger = logging.getLogger(__name__)

api = flask.Blueprint('api', __name__)


#######################################################################
#                             Marshalling                             #
#######################################################################

class PositionSchema(marshmallow.Schema):
    x = marshmallow.fields.Integer()
    y = marshmallow.fields.Integer()
    z = marshmallow.fields.Integer()


class ActionSchema(marshmallow.Schema):
    pass


class NavigateSchema(marshmallow.Schema):
    background = marshmallow.fields.String()
    current_position = marshmallow.fields.Nested(PositionSchema)
    available_actions = marshmallow.fields.Nested(ActionSchema, many=True)


def marshal(data, schema: marshmallow.Schema = None, is_json: bool = True):
    if schema:
        is_list = isinstance(data, list)
        data = schema.dump(data, many=is_list)
    return json.dumps(data) if is_json else data


#######################################################################
#                               Routes                                #
#######################################################################


@api.route('/current')
def current():
    current_pos = actions.get_current_position()

    tile = builder.get_or_create_tile(current_pos)
    background = tile['background']

    # Build response
    resp = {
        'background': background,
        'current_position': current_pos,
        'available_actions': ['a', 'b', 'c'],
    }
    return marshal(resp, schema=NavigateSchema()), 200


@api.route('/navigate')
def navigate():
    direction_str = flask.request.args.get('direction')
    direction = Direction.from_string(direction_str)

    current_pos = actions.get_current_position()
    target_pos = current_pos.translate(direction)

    current_tile = database.get_tile(current_pos)
    if current_tile['sides'][direction.value]['is_blocked']:
        # The way is shut
        return 'The way is shut', 403

    # Fetch tile and update position
    tile = builder.get_or_create_tile(target_pos)
    background = tile['background']
    database.update_current_position(target_pos)
    current_pos = target_pos

    # TODO: Calculate available actions

    # Build response
    resp = {
        'background': background,
        'current_position': current_pos,
        'available_actions': ['a', 'b', 'c'],
    }
    return marshal(resp, schema=NavigateSchema()), 200


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

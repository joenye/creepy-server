import flask
import logging

import database
from common.direction import Direction
from common.point import Point
from tiles import builder, cavern, tunnel

logger = logging.getLogger(__name__)

api = flask.Blueprint('api', __name__)


@api.route('/current')
def current():
    current_pos = get_current_position()

    tile = builder.get_or_create_tile(current_pos)
    background = tile['background']

    return flask.Response(background, status=200, mimetype='text/xml')


@api.route('/navigate')
def navigate():
    direction_str = flask.request.args.get('direction')
    direction = Direction.from_string(direction_str)

    current_pos = get_current_position()
    target_pos = current_pos.translate(direction)

    current_tile = database.get_tile(current_pos)
    if current_tile['sides'][direction.value]['is_blocked']:
        # The way is shut
        return 'The way is shut', 403

    # Fetch tile and update position
    tile = builder.get_or_create_tile(target_pos)
    background = tile['background']
    database.update_current_position(target_pos)

    # TODO: Need to additionally return the current position and available actions
    return flask.Response(background, status=200, mimetype='text/xml')


@api.route('/debug/cavern')
def get_cavern():
    file_dir, filename = cavern.render_tile()
    return flask.send_from_directory(file_dir, filename)


@api.route('/debug/tunnel')
def get_tunnel():
    try:
        file_dir, filename = tunnel.render_tile()
    # TODO: Fix tile-generation bug so no need for this
    except ValueError:
        return get_tunnel()

    return flask.send_from_directory(file_dir, filename)


# TODO: Refactor into actions/engine along with other business logic in here
def get_current_position():
    current_pos = database.get_current_position()
    if current_pos:
        return current_pos

    start_pos = Point(0, 0, 0)
    database.update_current_position(start_pos)
    return database.get_current_position()

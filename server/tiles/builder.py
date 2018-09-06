import random
import typing
import logging

import utils
import database
from common.direction import Direction
from common.point import Point
from tiles import tunnel, cavern
from tiles.common.exit_config import ExitConfig

logger = logging.getLogger(__name__)


def get_or_create_tile(target: Point) -> dict:
    existing_tile = database.get_tile(target)
    if existing_tile:
        return existing_tile

    new_tile = _create_tile(target)
    database.insert_tile(target, new_tile)

    return new_tile


def _create_tile(target: Point) -> dict:
    tile = {}
    tile['is_visited'] = False
    tile['sides'] = _create_sides(target)

    exit_configs = []
    for _, direction_str in enumerate(side for side in tile['sides']):
        is_blocked = tile['sides'][direction_str]['is_blocked']
        edge_position = tile['sides'][direction_str]['edge_position']
        direction = Direction.from_string(direction_str)
        exit_configs.append(ExitConfig(direction, edge_position, is_blocked))

    tile_gen = _get_tile_generator()
    file_dir, filename = _render_tile(tile_gen, exit_configs)
    tile['background'] = utils.load_text_file(file_dir, filename)

    return tile


def _render_tile(tile_gen, exit_configs):
    """Retries rendering on errors.

    """
    try:
        return tile_gen.render_tile(exit_configs)
    except ValueError:
        return _render_tile(tile_gen, exit_configs)


def _get_tile_generator() -> callable:
    prob_cavern = 3
    return cavern if random.randint(1, 10) <= prob_cavern else tunnel


def _create_sides(target: Point) -> typing.Dict[Direction, dict]:
    sides = {}

    for direction in Direction:
        side = {'is_blocked': _random_is_blocked()}

        adjacent_tile = database.get_tile(target.translate(direction))
        if adjacent_tile:
            opposite_dir = Direction.mirror_of(direction)
            opposite_edge_pos = adjacent_tile['sides'][opposite_dir.value]['edge_position']
            side['edge_position'] = opposite_edge_pos
        else:
            side['edge_position'] = _random_edge_position(direction)

        sides[direction.value] = side

    # Retry on 3+ blocked exits
    num_blocked = sum([s['is_blocked'] for s in sides.values()])
    if num_blocked >= 3:
        return _create_sides(target)

    return sides


def _random_is_blocked() -> bool:
    return random.randint(1, 10) <= 2  # 20% probability


def _random_edge_position(direction: Direction) -> int:
    if direction in {Direction.UP, Direction.DOWN}:
        return random.randint(1, 4)
    else:
        return random.randint(1, 3)

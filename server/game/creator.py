"""
High-level abstraction over tile generation. Cares about "balancing" the game.

"""
import random

import database
from common.point import Point
from common.enum import TileType
from game import builder


def get_or_create_tile(target: Point) -> dict:
    existing_tile = database.get_tile(target)
    if existing_tile:
        return existing_tile

    return _create_tile(target)


def _create_tile(target):
    new_tile = builder.TileBuilder(target, _get_tile_type(), _get_prob_blockage())()

    # TODO: Entity / card logic goes here

    database.insert_tile(target, new_tile)
    return new_tile


def _get_tile_type() -> callable:
    prob_cavern = 0.3
    return TileType.CAVERN if random.randint(1, 10) <= (prob_cavern * 10) else TileType.TUNNEL


def _get_prob_blockage() -> bool:
    return 0.2

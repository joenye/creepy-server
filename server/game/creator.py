"""
High-level abstraction over tile generation. Cares about "balancing" the game.

"""
import random

from common.point import Point
from common.enum import TileType
from game import builder
from game import database


def get_or_create_tile(target: Point) -> dict:
    existing_tile = database.get_tile(target)
    if existing_tile:
        return existing_tile

    return _create_tile(target)


def _create_tile(target):
    new_tile = builder.TileBuilder(target, _tile_type(), _prob_blockage())()

    # TODO: Entity / card logic goes here

    database.insert_tile(target, new_tile)
    return new_tile


def _tile_type() -> TileType:
    prob_cavern = 0.3
    return TileType.CAVERN if random.randint(1, 10) <= (prob_cavern * 10) else TileType.TUNNEL


def _prob_blockage() -> float:
    return 0.2


def _prob_stairs() -> float:
    return 0.05

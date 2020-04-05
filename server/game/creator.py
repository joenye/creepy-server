"""
High-level abstraction over tile generation. Cares about "balancing" the game.

"""
import random
import logging

from common.point import Point
from common.enum import TileType, EntityType
from game import builder
from game import database


LOGGER = logging.getLogger(__name__)


def get_or_create_tile(target: Point) -> dict:
    existing_tile = database.get_tile(target)
    if existing_tile:
        return existing_tile

    return _create_tile(target)


def _create_tile(target) -> dict:
    new_tile = builder.TileBuilder(target, _tile_type(), _prob_blockage())()
    new_tile = _add_entities(new_tile)
    new_tile = _add_cards(new_tile)

    database.insert_or_update_tile(target, new_tile)
    return new_tile


def _add_entities(tile) -> dict:
    used = set()
    tile["entities"] = {}
    candidates = tile["entity_candidates"][:]
    random.shuffle(candidates)
    for pos in [Point.deserialize(c) for c in candidates]:
        unused = [e for e in EntityType.all() if e not in used]
        random.shuffle(unused)
        for entity in unused:
            if random.uniform(0, 1) > _ENTITY_PROBS[entity]:
                continue
            tile["entities"][entity.value] = {"pos": pos}
            used.add(entity)
            break

    return tile


def _add_cards(tile) -> dict:
    return tile


_ENTITY_PROBS = {
    EntityType.STAIRS_UP: 0.025,
    EntityType.STAIRS_UP_SECRET: 0,
    EntityType.STAIRS_DOWN: 0.025,
    EntityType.STAIRS_DOWN_SECRET: 0,
}


def _tile_type() -> TileType:
    prob_cavern = 0.3
    return TileType.CAVERN if random.uniform(0, 1) <= prob_cavern else TileType.TUNNEL


_TILE_PROBS = {TileType.CAVERN: 0.3, TileType.TUNNEL: 0.7}


def _prob_blockage() -> float:
    return 0.2


def _prob_stairs() -> float:
    return 0.05

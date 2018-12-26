"""
High-level abstraction over tile generation. Cares about "balancing" the game.

"""
import random
import logging

from common.point import Point
from common.enum import TileType, EntityType
from game import builder
from game import database


logger = logging.getLogger(__name__)


def get_or_create_tile(target: Point) -> dict:
    existing_tile = database.get_tile(target)
    if existing_tile:
        return existing_tile

    return _create_tile(target)


def _create_tile(target) -> dict:
    new_tile = builder.TileBuilder(target, _tile_type(), _prob_blockage())()
    new_tile = _add_entities(new_tile)
    new_tile = _add_cards(new_tile)

    database.insert_tile(target, new_tile)
    return new_tile


def _add_entities(tile) -> dict:
    used = set()
    tile['entities'] = {}
    candidates = tile['entity_candidates'][:]
    random.shuffle(candidates)
    for pos in candidates:
        unused = [e for e in EntityType.all() if e not in used]
        random.shuffle(unused)
        for entity in unused:
            if random.uniform(0, 1) > _entity_probs[entity]:
                continue
            tile['entities'][pos] = entity.value
            used.add(entity)
            break

    return tile


def _add_cards(tile) -> dict:
    return tile


_entity_probs = {
    EntityType.STAIRS_UP: 0.05,
    EntityType.STAIRS_UP_SECRET: 0,
    EntityType.STAIRS_DOWN: 0.05,
    EntityType.STAIRS_DOWN_SECRET: 0,
}


def _tile_type() -> TileType:
    prob_cavern = 0.3
    return TileType.CAVERN if random.uniform(0, 1) <= prob_cavern else TileType.TUNNEL


_tile_probs = {
    TileType.CAVERN: 0.3,
    TileType.TUNNEL: 0.7
}


def _prob_blockage() -> float:
    return 0.2


def _prob_stairs() -> float:
    return 0.05

import copy
import logging
import collections

import pymongo

from common import settings
from common.point import Point

LOGGER = logging.getLogger(__name__)

_CLIENT = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)


def get_current_position() -> Point:
    creepy_db = _CLIENT["creepy"]
    collection = creepy_db["tiles"]

    doc = collection.find_one({}, {"session.current_position": 1})

    if doc:
        return Point.deserialize(doc["session"]["current_position"])
    return None


def update_current_position(new_pos: Point) -> Point:
    creepy_db = _CLIENT["creepy"]
    collection = creepy_db["tiles"]

    updates = {"session.current_position": new_pos.serialize()}
    return collection.update_one({}, {"$set": updates}, upsert=True)


def get_all_visited_tiles():
    """
    Returns a dict mapping from floor to a list of visited tiles
    """
    creepy_db = _CLIENT["creepy"]
    collection = creepy_db["tiles"]

    doc = collection.find_one({f"session.floors": {"$exists": True}})
    if not doc:
        return None

    floor_to_tiles = collections.defaultdict(list)
    floors = doc["session"]["floors"]
    for floor, val in floors.items():
        for pos, tile in val["tiles"].items():
            if not tile["is_visited"]:
                continue

            point = Point.deserialize(pos)
            point.z = int(floor)
            tile["position"] = point
            floor_to_tiles[floor].append(_deserialize_pos(tile))

    return floor_to_tiles


def get_tile(point: Point):
    creepy_db = _CLIENT["creepy"]
    collection = creepy_db["tiles"]

    str_floor = str(point.z)
    str_point = point.serialize(strip_z=True)

    doc = collection.find_one(
        {f"session.floors.{str_floor}.tiles.{str_point}": {"$exists": True}}
    )
    if not doc:
        return None

    return _deserialize_pos(doc["session"]["floors"][str_floor]["tiles"][str_point])


def insert_or_update_tile(point: Point, tile: dict):
    creepy_db = _CLIENT["creepy"]
    collection = creepy_db["tiles"]

    str_floor = str(point.z)
    str_point = point.serialize(strip_z=True)

    tile_cpy = _serialize_pos(copy.deepcopy(tile))
    updates = {f"session.floors.{str_floor}.tiles.{str_point}": tile_cpy}

    return collection.update_one({}, {"$set": updates}, upsert=True)


def _serialize_pos(obj: dict) -> dict:
    """Recursively serialize all `Point` instances"""

    def update(obj):
        for key, val in obj.items():
            if isinstance(val, dict):
                obj[key] = update(obj.get(key, {}))
            elif isinstance(val, Point):
                obj[key] = obj[key].serialize()
        return obj

    return update(obj)


def _deserialize_pos(obj: dict) -> dict:
    """Recursively deserialize all `Point` instances"""

    def update(obj):
        for key, val in obj.items():
            if isinstance(val, dict):
                obj[key] = update(obj.get(key, {}))
            elif isinstance(val, str) and "," in str(val):
                obj[key] = Point.deserialize(obj[key])
        return obj

    return update(obj)

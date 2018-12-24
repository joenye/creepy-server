import logging
import pymongo
import collections

from common import settings
from common.point import Point

logger = logging.getLogger(__name__)

_client = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)


def get_current_position() -> Point:
    db = _client['creepy']
    collection = db['tiles']

    doc = collection.find_one({}, {'session.current_position': 1})

    if doc:
        return Point.deserialize(doc['session']['current_position'])
    else:
        return None


def update_current_position(new_pos: Point) -> Point:
    db = _client['creepy']
    collection = db['tiles']

    updates = {'session.current_position': new_pos.serialize()}
    return collection.update_one({}, {'$set': updates}, upsert=True)


def get_all_visited_tiles():
    """
    Returns a dict mapping from floor to a list of visited tiles
    """
    db = _client['creepy']
    collection = db['tiles']

    doc = collection.find_one({
        f"session.floors": {'$exists': True}
    })
    if not doc:
        return None

    floor_to_tiles = collections.defaultdict(list)
    floors = doc['session']['floors']
    for floor, val in floors.items():
        for pos, tile in val['tiles'].items():
            if not tile['is_visited']:
                continue

            point = Point.deserialize(pos)
            point.z = int(floor)
            tile['position'] = point
            floor_to_tiles[floor].append(tile)

    return floor_to_tiles


def get_tile(point: Point):
    db = _client['creepy']
    collection = db['tiles']

    str_floor = str(point.z)
    str_point = point.serialize(strip_z=True)

    doc = collection.find_one({
        f"session.floors.{str_floor}.tiles.{str_point}": {'$exists': True}
    })
    if not doc:
        return None

    return doc['session']['floors'][str_floor]['tiles'][str_point]


def insert_tile(point: Point, tile: dict):
    db = _client['creepy']
    collection = db['tiles']

    str_floor = str(point.z)
    str_point = point.serialize(strip_z=True)

    updates = {f"session.floors.{str_floor}.tiles.{str_point}": tile}

    return collection.update_one({}, {'$set': updates}, upsert=True)

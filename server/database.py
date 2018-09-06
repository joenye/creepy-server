import logging
import pymongo

import settings
from common.point import Point

logger = logging.getLogger(__name__)

_client = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)


def get_current_position() -> Point:
    db = _client['creepy']
    collection = db['tiles']

    cursor = collection.find_one({}, {'session.current_position': 1})

    if cursor:
        return Point.deserialize(cursor['session']['current_position'])
    else:
        return None


def update_current_position(new_pos: Point) -> Point:
    db = _client['creepy']
    collection = db['tiles']

    updates = {'session.current_position': new_pos.serialize()}
    return collection.update_one({}, {'$set': updates}, upsert=True)


def get_tile(point: Point):
    db = _client['creepy']
    collection = db['tiles']

    str_floor = str(point.z)
    str_point = point.serialize(strip_z=True)

    cursor = collection.find_one({
        f"session.floors.{str_floor}.tiles.{str_point}": {'$exists': True}
    })

    if cursor:
        return cursor['session']['floors'][str_floor]['tiles'][str_point]

    return None


def insert_tile(point: Point, tile: dict):
    db = _client['creepy']
    collection = db['tiles']

    str_floor = str(point.z)
    str_point = point.serialize(strip_z=True)

    updates = {f"session.floors.{str_floor}.tiles.{str_point}": tile}

    return collection.update_one({}, {'$set': updates}, upsert=True)

from enum import Enum


class ClientAction(Enum):
    NAVIGATE = 'navigate'

    REFRESH_ALL = 'refresh_all'
    REFRESH_CURRENT = 'refresh_current'
    REFRESH_FLOOR = 'refresh_floor'

    @classmethod
    def all(cls):
        return [a for a in cls]

    @classmethod
    def values(cls):
        return [d.value for d in cls]


class TileType(Enum):
    TUNNEL = 'tunnel'
    CAVERN = 'cavern'


class EntityType(Enum):
    STAIRS_UP = 'stairs_up'
    STAIRS_DOWN = 'stairs_down'

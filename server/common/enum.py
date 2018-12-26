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
        return [a.value for a in cls]


class TileType(Enum):
    TUNNEL = 'tunnel'
    CAVERN = 'cavern'

    @classmethod
    def all(cls):
        return [t for t in cls]

    @classmethod
    def values(cls):
        return [t.value for t in cls]


class EntityType(Enum):
    STAIRS_UP = 'stairs_up'
    STAIRS_UP_SECRET = 'stairs_up_secret'
    STAIRS_DOWN = 'stairs_down'
    STAIRS_DOWN_SECRET = 'stairs_down_secret'

    @classmethod
    def all(cls):
        return [t for t in cls]

    @classmethod
    def values(cls):
        return [t.value for t in cls]

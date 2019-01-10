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


class Direction(Enum):
    UP = 'up'
    RIGHT = 'right'
    DOWN = 'down'
    LEFT = 'left'

    ABOVE = 'above'
    BELOW = 'below'

    @classmethod
    def from_string(cls, value: str):
        if value == cls.UP.value:
            return Direction.UP
        if value == cls.RIGHT.value:
            return Direction.RIGHT
        if value == cls.DOWN.value:
            return Direction.DOWN
        if value == cls.LEFT.value:
            return Direction.LEFT
        if value == cls.ABOVE.value:
            return Direction.ABOVE
        if value == cls.BELOW.value:
            return Direction.BELOW

    @classmethod
    def to_nesw(cls, value: str):
        if value == cls.UP.value:
            return 'north'
        if value == cls.RIGHT.value:
            return 'east'
        if value == cls.DOWN.value:
            return 'south'
        if value == cls.LEFT.value:
            return 'west'

        raise ValueError(f"{value} is not a valid {cls.__name__}")

    @classmethod
    def mirror_of(cls, direction):
        if direction == cls.UP:
            return cls.DOWN
        if direction == cls.RIGHT:
            return cls.LEFT
        if direction == cls.DOWN:
            return cls.UP
        if direction == cls.LEFT:
            return cls.RIGHT

    @classmethod
    def clockwise_of(cls, direction):
        if direction == cls.UP:
            return cls.RIGHT
        if direction == cls.RIGHT:
            return cls.DOWN
        if direction == cls.DOWN:
            return cls.LEFT
        if direction == cls.LEFT:
            return cls.UP

    @classmethod
    def anticlockwise_of(cls, direction):
        if direction == cls.UP:
            return cls.LEFT
        if direction == cls.RIGHT:
            return cls.UP
        if direction == cls.DOWN:
            return cls.RIGHT
        if direction == cls.LEFT:
            return cls.DOWN

    @classmethod
    def all(cls):
        return [d for d in cls]

    @classmethod
    def all_nesw(cls):
        return [cls.UP, cls.RIGHT, cls.DOWN, cls.LEFT]

    @classmethod
    def values(cls):
        return [d.value for d in cls]

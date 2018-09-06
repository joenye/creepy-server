import enum


class Direction(enum.Enum):
    UP = 'up'
    RIGHT = 'right'
    DOWN = 'down'
    LEFT = 'left'

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

import enum
from common.direction import Direction


class PlayerAction(enum.Enum):
    NAVIGATE_UP = 'navigate_up'
    NAVIGATE_RIGHT = 'navigate_right'
    NAVIGATE_DOWN = 'navigate_down'
    NAVIGATE_LEFT = 'navigate_left'

    @classmethod
    def navigate_from_side(cls, side: str):
        if side == Direction.UP.value:
            return cls.NAVIGATE_UP
        if side == Direction.RIGHT.value:
            return cls.NAVIGATE_RIGHT
        if side == Direction.DOWN.value:
            return cls.NAVIGATE_DOWN
        if side == Direction.LEFT.value:
            return cls.NAVIGATE_LEFT

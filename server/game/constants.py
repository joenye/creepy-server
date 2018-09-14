import enum


class Action(enum.Enum):
    # Game
    NAVIGATE = 'navigate'

    # Data
    REFRESH_ALL = 'refresh_all'
    REFRESH_CURRENT = 'refresh_current'
    REFRESH_FLOOR = 'refresh_floor'

    @classmethod
    def all(cls):
        return [a for a in cls]

    @classmethod
    def values(cls):
        return [d.value for d in cls]

import database
from common.point import Point


def get_current_position():
    current_pos = database.get_current_position()
    if current_pos:
        return current_pos

    start_pos = Point(0, 0, 0)
    database.update_current_position(start_pos)
    return database.get_current_position()

"""Dungeon Master module which provides top-level game actions"""
import database
from common.point import Point
from constants import PlayerAction


def get_or_update_current_position():
    current_pos = database.get_current_position()
    if current_pos:
        return current_pos

    default_pos = Point(0, 0, 0)
    database.update_current_position(default_pos)
    return default_pos


def get_available_actions():
    current_pos = get_or_update_current_position()
    current_tile = database.get_tile(current_pos)

    actions = []
    for side, vals in current_tile['sides'].items():
        if not vals['is_blocked']:
            actions.append(PlayerAction.navigate_from_side(side).value)

    return actions

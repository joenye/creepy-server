"""Dungeon Master module provides top-level game actions"""
import logging

import database
from common.point import Point
from common.direction import Direction
from game import builder, errors
from game.constants import Action


logger = logging.getLogger(__name__)


def get_or_update_current_position():
    current_pos = database.get_current_position()
    if current_pos:
        return current_pos

    default_pos = Point(0, 0, 0)
    database.update_current_position(default_pos)
    return default_pos


def get_available_actions():
    current_pos = get_or_update_current_position()
    current_tile = builder.get_or_create_tile(current_pos)

    actions = []
    for side, vals in current_tile['sides'].items():
        if not vals['is_blocked']:
            actions.append(Action.NAVIGATE)
            break

    return actions


def get_target_dir(current_pos: Point, target_pos):
    for direction in Direction.all():
        if current_pos.translate(direction) == target_pos:
            return direction

    return None


def navigate(target_pos: Point):
    current_pos = get_or_update_current_position()
    logger.info(
        "Received request to navigate: "
        f"current_pos={current_pos}, target_pos={target_pos}"
    )

    # Validate this action is possible
    available_actions = get_available_actions()
    if Action.NAVIGATE not in available_actions:
        raise errors.InvalidAction("You can't navigate from where you are")

    if current_pos == target_pos:
        raise errors.InvalidAction("You're already on that tile")

    # Validate can reach the tile
    target_dir = get_target_dir(current_pos, target_pos)
    if not target_dir:
        raise errors.InvalidAction('That tile is too far away')

    # Validate current tile is not blocked on this side
    current_tile = builder.get_or_create_tile(current_pos)
    if current_tile['sides'][target_dir.value]['is_blocked']:
        raise errors.InvalidAction('The way is shut from this side')

    # Validate target tile is not blocked on the other side
    target_tile = builder.get_or_create_tile(target_pos)
    if target_tile['sides'][Direction.mirror_of(target_dir).value]['is_blocked']:
        raise errors.InvalidAction('The way is shut from the other side')

    # Fetch (or create) tile and update position
    tile = builder.get_or_create_tile(target_pos)
    database.update_current_position(target_pos)

    logger.info(f"Successfully navigated: target_pos={target_pos}")
    return tile

"""Available client actions"""
import logging

from common.point import Point
from common.enum import ClientAction
from common.enum import Direction
from game import database
from game import creator, errors as game_errors


LOGGER = logging.getLogger(__name__)


def get_or_update_current_position():
    current_pos = database.get_current_position()
    if current_pos:
        return current_pos

    default_pos = Point(0, 0, 0)
    database.update_current_position(default_pos)
    return default_pos


def get_available_actions():
    current_pos = get_or_update_current_position()
    current_tile = creator.get_or_create_tile(current_pos)

    actions = []
    for _side, vals in current_tile["sides"].items():
        if not vals["is_blocked"]:
            actions.append(ClientAction.NAVIGATE)
            break
        # TODO: Other actions go here

    return actions


def get_target_dir(current_pos: Point, target_pos):
    for direction in Direction.all():
        if current_pos.translate(direction) == target_pos:
            return direction

    return None


def get_all_visited_tiles():
    return database.get_all_visited_tiles()


def create_initial_tile():
    current_pos = get_or_update_current_position()
    LOGGER.info("Received request to create initial tile: current_pos= %s", current_pos)
    tile = creator.get_or_create_tile(current_pos)
    tile["is_visited"] = True
    database.insert_or_update_tile(current_pos, tile)
    database.update_current_position(current_pos)
    LOGGER.info("Successfully created initial tile: current_pos=%s", current_pos)
    return tile


def navigate(target_pos: Point):
    current_pos = get_or_update_current_position()
    LOGGER.info(
        "Received request to navigate: current_pos=%s, target_pos=%s",
        current_pos,
        target_pos,
    )

    # Validate this action is possible
    available_actions = get_available_actions()
    if ClientAction.NAVIGATE not in available_actions:
        raise game_errors.InvalidAction("You can't navigate from where you are")

    if current_pos == target_pos:
        raise game_errors.InvalidAction("You're already on that tile")

    # Validate can reach the tile
    target_dir = get_target_dir(current_pos, target_pos)
    if not target_dir:
        raise game_errors.InvalidAction("That tile is too far away")

    current_tile = creator.get_or_create_tile(current_pos)
    target_tile = creator.get_or_create_tile(target_pos)
    if target_dir in Direction.all_nesw():
        # Validate current tile is not blocked on this side
        if current_tile["sides"][target_dir.value]["is_blocked"]:
            raise game_errors.InvalidAction("The way is shut from this side")
        # Validate target tile is not blocked on the other side
        if target_tile["sides"][Direction.mirror_of(target_dir).value]["is_blocked"]:
            raise game_errors.InvalidAction("The way is shut from the other side")
    else:
        # TODO: Validation when going up or down
        pass

    # Mark tile as visited (prevents user from refreshing and seeing adjacent tiles
    # which exist in the database but they have not accessed)
    target_tile["is_visited"] = True
    database.insert_or_update_tile(target_pos, target_tile)

    database.update_current_position(target_pos)

    LOGGER.info("Successfully navigated: target_pos=%s", target_pos)
    return target_tile

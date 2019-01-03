"""
Low-level abstraction over building tiles. Cares about retries and interfacing with
the underlying tile generating logic.

"""
import random
import logging
from typing import Dict

import renderer
from renderer.common.exit_config import ExitConfig
from game import database
from common import file_utils
from common.point import Point
from common.enum import TileType
from common.direction import Direction

logger = logging.getLogger(__name__)


class TileBuilder:
    def __init__(self, target: Point, tile_type: TileType, prob_blockage: float):
        self.target = target
        self.tile_type = tile_type
        self.prob_blockage = prob_blockage

    def __call__(self):
        tile = {}
        tile['is_visited'] = False
        tile['sides'] = self._create_sides()

        exit_configs = []
        for _, direction_str in enumerate(side for side in tile['sides']):
            is_blocked = tile['sides'][direction_str]['is_blocked']
            edge_position = tile['sides'][direction_str]['edge_position']
            direction = Direction.from_string(direction_str)
            exit_configs.append(ExitConfig(direction, edge_position, is_blocked))

        render_mod = renderer.get_renderer(self.tile_type)

        num_attempts = 0
        while True:
            try:
                file_dir, entities, filename = render_mod.render_tile(exit_configs)
                break
            except ValueError:
                # TODO: Fix root cause
                num_attempts += 1
                if num_attempts >= 10:
                    raise Exception(
                        f"Unexpected problem rendering tile: exit_configs={exit_configs}"
                    )
                logger.warn("Failed to render tile: exit_configs={exit_configs}")

        tile['entity_candidates'] = [p.serialize() for p in entities]
        tile['background'] = file_utils.load_text_file(file_dir, filename)
        return tile

    def _create_sides(self) -> Dict[Direction, dict]:
        sides = {}

        for direction in Direction.all_nesw():
            side = {'is_blocked': self._random_is_blocked()}

            adjacent_tile = database.get_tile(self.target.translate(direction))
            if adjacent_tile:
                opposite_dir = Direction.mirror_of(direction)
                opposite_edge_pos = adjacent_tile['sides'][opposite_dir.value]['edge_position']
                side['edge_position'] = opposite_edge_pos
            else:
                side['edge_position'] = self._random_edge_position(direction)

            sides[direction.value] = side

        # Retry on 3+ blocked exits
        num_blocked = sum([s['is_blocked'] for s in sides.values()])
        if num_blocked >= 3:
            return self._create_sides()

        return sides

    def _random_is_blocked(self) -> bool:
        return random.randint(1, 10) <= (self.prob_blockage * 10)

    def _random_edge_position(self, direction: Direction) -> int:
        if direction in {Direction.UP, Direction.DOWN}:
            return random.randint(1, 4)
        else:
            return random.randint(1, 3)

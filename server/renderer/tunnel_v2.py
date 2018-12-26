import os
import sys
import random
import typing

import svgwrite

package = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(package))

from common import settings
from common.point import Point
from common.direction import Direction as Dir
from renderer.common import exit, exit_config, rectangle, smoothing, tile


class Grid:
    """Overlay used for calculations. Elements are `rectangle.Rect` objects positioned in
    `Tile` coordinates, with their `Grid` position is expressed in `Grid` coordinates.

    """
    elements: typing.List[typing.List[Point]]

    def __init__(self, tile: tile.Tile) -> None:
        self.tile = tile
        self._generate()

    def get_all_rects(self) -> typing.List[rectangle.Rectangle]:
        return [y for x in self.elements for y in x]

    def get_all_rects_in_row(self, row_y) -> typing.List[rectangle.Rectangle]:
        return [rects[row_y] for rects in self.elements]

    def get_all_rects_in_column(self, column_x) -> typing.List[rectangle.Rectangle]:
        return [rect for rect in self.elements[column_x][:]]

    def get_rect_at(self, point: Point) -> rectangle.Rectangle:
        return self.elements[point.x][point.y]

    def _generate(self):
        rect_width = 100
        rect_height = 100

        self.width = (self.tile.width // rect_width) + 1
        self.height = (self.tile.height // rect_height) + 1

        self.elements = [[None for y in range(self.height)] for x in range(self.width)]

        for grid_y in range(0, self.height):
            for grid_x in range(0, self.width):
                x = (grid_x * rect_width) - rect_width / 2 if grid_x > 0 else 0
                y = (grid_y * rect_height) - rect_width / 2 if grid_y > 0 else 0

                x_adj = rect_width / 2 if grid_x in {0, self.width - 1} else rect_width
                y_adj = rect_height / 2 if grid_y in {0, self.height - 1} else rect_height

                rect = rectangle.Rectangle(
                    bl=Point(x, y),
                    br=Point(x + x_adj, y),
                    tl=Point(x, y + y_adj),
                    tr=Point(x + x_adj, y + y_adj)
                )

                self.elements[grid_x][grid_y] = rect


class Path:
    """Calculates and stores paths, which are collections of `Points` in `Grid`
    coordinates.

    """
    filled: typing.List[Point]
    exits: typing.Dict[Dir, exit.Exit]

    def __init__(self, grid_width: int, grid_height: int,
                 exits: typing.Dict[Dir, exit.Exit]) -> None:
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.exits = exits
        self._calculate_filled()

    def get_path_between(self, current: Point, target: Point,
                         path: typing.List[Point] = None) -> typing.List[Point]:
        """Finds a path between start and target. If two adjacent tiles are an equal
        distance from the target, then searches recursively.

        """
        if not path:
            path = [current]

        while current != target:
            adjacents = self._get_all_adjacent(current)

            candidates = [a for a in adjacents if a not in path and a in self.filled]
            # Sad halt condition
            if not candidates:
                return None

            dists = [Point.distance_between(c, target) for c in candidates]

            min_ = min(dists)
            if dists.count(min_) > 1:
                equidistants = [c for i, c in enumerate(candidates) if dists[i] == min_]
                for equi in equidistants:
                    # Begin recursive search
                    remaining_path = self.get_path_between(equi.copy(), target, path.copy())

                    # Happy halt condition
                    if remaining_path:
                        return remaining_path

            nex = candidates[dists.index(min_)]

            path.append(nex)
            current = nex

        # Happy halt condition
        return path

    def _calculate_filled(self):
        self.filled = [exit_.point for exit_ in self.exits.values()]

        # Randomise start direction
        exit_items = list(self.exits.items())
        random.shuffle(exit_items)

        for direction, exit_ in exit_items:
            start = exit_
            target_dir = Dir.mirror_of(direction)
            target = self.exits[target_dir]

            if start.is_blocked:
                continue

            if target.is_blocked:
                # Keep looking clockwise until we find a non-blocked exit
                found = False
                while not found:
                    target_dir = Dir.clockwise_of(target_dir)
                    target = self.exits[target_dir]
                    if not target.is_blocked:
                        found = True

            self.filled += self._calculate_path(start.point, target.point)

        # If 4 rects form a square, try again
        if self._is_square_present_in_filled():
            self._calculate_filled()

    def _calculate_path(self, start: Point, target: Point) -> typing.List[Point]:
        """Stops when we reach the target or we reach a grid position already filled.

        """
        path: typing.List = []
        current = start

        while current != target:
            candidates = self._get_path_candidates(current, target)

            if any([c in self.filled for c in candidates]):
                return path

            valid_candidates = []
            for candidate in candidates:
                if not self._is_on_edge(candidate):
                    valid_candidates.append(candidate)

            nex = random.choice(valid_candidates)
            path.append(nex)
            current = nex

        return path

    def _get_path_candidates(self, current: Point, target: Point) -> typing.List[Point]:
        """Calculate candidate directions to get closer to the target. Returns a list of
        either one or two candidate directions.

        """
        candidates = []

        if target.y > current.y:
            candidates.append(current.translate(Dir.UP))
        if target.x > current.x:
            candidates.append(current.translate(Dir.RIGHT))
        if target.y < current.y:
            candidates.append(current.translate(Dir.DOWN))
        if target.x < current.x:
            candidates.append(current.translate(Dir.LEFT))

        return candidates

    def _is_on_edge(self, point: Point) -> bool:
        right_left = {0, self.grid_width - 1}
        up_down = {0, self.grid_height - 1}

        return point.x in right_left or point.y in up_down

    def _is_square_present_in_filled(self) -> bool:
        left_right_pairs = []
        for top_left in self.filled:
            for top_right in self.filled:
                if top_right.x == top_left.x + 1 and top_right.y == top_left.y:
                    left_right_pairs.append((top_left, top_right))

        for top_left, top_right in left_right_pairs:
            bottom_left = top_left.translate(Dir.DOWN)
            bottom_right = top_right.translate(Dir.DOWN)

            if (bottom_left, bottom_right) in left_right_pairs:
                return True

        return False

    def _get_all_adjacent(self, current: Point) -> typing.List[Point]:
        candidates = []
        for direction in Dir:
            candidates.append(current.translate(direction))

        return candidates


class ElbowMaker:
    # Point is in tile coordinates
    elbows: typing.Dict[Dir, typing.List[Point]] = {}

    def __init__(self, grid: Grid, path: Path) -> None:
        self.grid = grid
        self.path = path
        self._calculate_elbows()

    def connected_elbows(self) -> (typing.List[Point], typing.List[typing.List[Point]]):
        connected: typing.List = []
        stubs: typing.List = []

        for dir_ in Dir:
            if self.path.exits[dir_].is_blocked:
                stubs.append(self.elbows[dir_])
            else:
                connected += self.elbows[dir_]

        return connected, stubs

    def _calculate_elbows(self):
        for direction, start in self.path.exits.items():
            if start.is_blocked:
                # Add exit and intersection points
                elbow = []
                offset = 0
                if direction == Dir.LEFT:
                    inward_dir = Dir.mirror_of(direction)
                    is_stub = start.point.translate(inward_dir) in self.path.filled
                    start_rect = self.grid.get_rect_at(start.point)
                    elbow += [
                        start_rect.tl.translate(direction, offset),
                        (
                            start_rect.tr.translate(direction, start_rect.width() / 2)
                            if is_stub else start_rect.tr
                        ),
                        (
                            start_rect.br.translate(direction, start_rect.width() / 2)
                            if is_stub else start_rect.br
                        ),
                        start_rect.bl.translate(direction, offset)
                    ]
                if direction == Dir.UP:
                    inward_dir = Dir.mirror_of(direction)
                    is_stub = start.point.translate(inward_dir) in self.path.filled
                    start_rect = self.grid.get_rect_at(start.point)
                    elbow += [
                        start_rect.tr.translate(direction, offset),
                        (
                            start_rect.br.translate(direction, start_rect.width() / 2)
                            if is_stub else start_rect.br
                        ),
                        (
                            start_rect.bl.translate(direction, start_rect.width() / 2)
                            if is_stub else start_rect.bl
                        ),
                        start_rect.tl.translate(direction, offset)
                    ]
                if direction == Dir.RIGHT:
                    inward_dir = Dir.mirror_of(direction)
                    is_stub = start.point.translate(inward_dir) in self.path.filled
                    start_rect = self.grid.get_rect_at(start.point)
                    elbow += [
                        start_rect.br.translate(direction, offset),
                        (
                            start_rect.bl.translate(direction, start_rect.width() / 2)
                            if is_stub else start_rect.bl
                        ),
                        (
                            start_rect.tl.translate(direction, start_rect.width() / 2)
                            if is_stub else start_rect.tl
                        ),
                        start_rect.tr.translate(direction, offset)
                    ]
                if direction == Dir.DOWN:
                    inward_dir = Dir.mirror_of(direction)
                    is_stub = start.point.translate(inward_dir) in self.path.filled
                    start_rect = self.grid.get_rect_at(start.point)
                    elbow += [
                        start_rect.bl.translate(direction, offset),
                        (
                            start_rect.bl.translate(direction, start_rect.width() / 2)
                            if is_stub else start_rect.tl
                        ),
                        (
                            start_rect.tl.translate(direction, start_rect.width() / 2)
                            if is_stub else start_rect.tr
                        ),
                        start_rect.br.translate(direction, offset)
                    ]

            else:
                # Add start exit point
                elbow = []
                offset = 30
                if direction == Dir.LEFT:
                    elbow.append(
                        self.grid.get_rect_at(start.point).tl.translate(Dir.LEFT, offset)
                    )
                if direction == Dir.UP:
                    elbow.append(
                        self.grid.get_rect_at(start.point).tr.translate(Dir.UP, offset)
                    )
                if direction == Dir.RIGHT:
                    elbow.append(
                        self.grid.get_rect_at(start.point).br.translate(Dir.RIGHT, offset)
                    )
                if direction == Dir.DOWN:
                    elbow.append(
                        self.grid.get_rect_at(start.point).bl.translate(Dir.DOWN, offset)
                    )

                # Keep looking clockwise until we find a non-blocked exit
                found = False
                target_dir = direction
                while not found:
                    target_dir = Dir.clockwise_of(target_dir)
                    target = self.path.exits[target_dir]
                    if not target.is_blocked:
                        found = True

                path = self.path.get_path_between(start.point, target.point)

                # Add intersections
                for index, current in enumerate(path):
                    if index == 0 or index == len(path) - 1:
                        continue

                    prev = path[index - 1]
                    nex = path[index + 1]
                    prev_intersect = elbow[-1]

                    intersection = self._calculate_intersection(
                        prev, current, nex, prev_intersect
                    )
                    if not intersection:
                        continue

                    elbow.append(intersection)

                # Add target exit point
                if target_dir == Dir.LEFT:
                    elbow.append(
                        self.grid.get_rect_at(target.point).bl.translate(Dir.LEFT, offset)
                    )
                if target_dir == Dir.UP:
                    elbow.append(
                        self.grid.get_rect_at(target.point).tl.translate(Dir.UP, offset)
                    )
                if target_dir == Dir.RIGHT:
                    elbow.append(
                        self.grid.get_rect_at(target.point).tr.translate(Dir.RIGHT, offset)
                    )
                if target_dir == Dir.DOWN:
                    elbow.append(
                        self.grid.get_rect_at(target.point).br.translate(Dir.DOWN, offset)
                    )

            # Insert points between
            elbow_cpy = elbow.copy()
            offset = 1
            for index, current in enumerate(elbow_cpy):
                if index == len(elbow_cpy) - 1:
                    break

                nex = elbow_cpy[index + 1]
                points_between = self._calculate_points_between(current, nex)
                elbow = elbow[:index + offset] + points_between + elbow[index + offset:]

                if index != 0:
                    elbow.pop(index + offset - 1)
                    offset -= 1

                offset += len(points_between)

            self.elbows[direction] = elbow

    def _calculate_intersection(self, prev: Point, current: Point, nex: Point,
                                prev_intersect: Point) -> Point:
        if nex.x == prev.x or nex.y == prev.y:
            # No bend, so return early
            return None

        tl = self.grid.get_rect_at(current).tl
        br = self.grid.get_rect_at(current).br

        tr = self.grid.get_rect_at(current).tr
        bl = self.grid.get_rect_at(current).bl

        if nex.x > prev.x and nex.y > prev.y:
            if current.y > prev.y:  # Up-Right
                for corner in tl, br:
                    if corner.x == prev_intersect.x:
                        return corner
            if current.x > prev.x:  # Right-Up
                for corner in tl, br:
                    if corner.y == prev_intersect.y:
                        return corner

        if nex.x > prev.x and nex.y < prev.y:
            if current.x > prev.x:  # Right-Down
                for corner in tr, bl:
                    if corner.y == prev_intersect.y:
                        return corner
            if current.y < prev.y:  # Down-Right
                for corner in tr, bl:
                    if corner.x == prev_intersect.x:
                        return corner

        if nex.x < prev.x and nex.y < prev.y:
            if current.x < prev.x:  # Left-Down
                for corner in tl, br:
                    if corner.y == prev_intersect.y:
                        return corner
            if current.y < prev.y:  # Down-Left
                for corner in tl, br:
                    if corner.x == prev_intersect.x:
                        return corner

        if nex.x < prev.x and nex.y > prev.y:
            if current.x < prev.x:  # Left-Up
                for corner in tr, bl:
                    if corner.y == prev_intersect.y:
                        return corner
            if current.y > prev.y:  # Up-Left
                for corner in tr, bl:
                    if corner.x == prev_intersect.x:
                        return corner

    def _get_next_exit(self, current: Point, target: Point):
        candidates = []

        if target.y > current.y:  # Up
            candidates.append(Point(current.x, current.y + 1))
        if target.x > current.x:  # Right
            candidates.append(Point(current.x + 1, current.y))
        if target.y < current.y:  # Down
            candidates.append(Point(current.x, current.y - 1))
        if target.x < current.x:  # Left
            candidates.append(Point(current.x - 1, current.y))

        for candidate in candidates:
            if candidate in self.path.filled:
                return candidate

        raise Exception('should have found a filled exit')

    def _calculate_points_between(self, p1: Point, p2: Point) -> typing.List[Point]:
        x_mult, y_mult, dist = self._mults(p1, p2)
        allowed_variation = 10
        spacing = 30
        points = []

        i = spacing
        while i < dist:
            variation = random.randint(-allowed_variation, allowed_variation)
            point = Point(
                p1.x + (x_mult * i) + (variation if y_mult != 0 else 0),
                p1.y + (y_mult * i) + (variation if x_mult != 0 else 0)
            )
            points.append(point)

            i += spacing

        return points

    def _mults(self, p1: Point, p2: Point) -> (float, float, float):
        if p1.x == p2.x:
            x_mult = 0
            y_mult = self._int_sign(p2.y - p1.y)
            dist = abs(p1.y - p2.y)
        elif p1.y == p2.y:
            x_mult = self._int_sign(p2.x - p1.x)
            y_mult = 0
            dist = abs(p1.x - p2.x)
        else:
            y_mult = 0
            dist = 0
            # TODO: Fix so this doesn't happen - it currently happens quite frequently
            raise ValueError(f"p1 and p2 should share one coordinate: p1={p1}, p2={p2}")

        return x_mult, y_mult, dist

    def _int_sign(self, x):
        return bool(x > 0) - bool(x < 0)


def invert_y(point: Point) -> Point:
    # TODO: Write wrapper around dwg to invert automatically and handle boilerplate
    return point.x, 400 - point.y


def draw_debug(dwg: svgwrite.Drawing, path: Path, grid: Grid, elbows: ElbowMaker, entities):
    for index, filled_point in enumerate(path.filled):
        rect = grid.get_rect_at(filled_point)
        dwg.add(dwg.rect(
            insert=invert_y(rect.tl),
            size=(rect.tr.x - rect.tl.x, rect.tl.y - rect.bl.y),
            fill='grey',
        ))
        dwg.add(dwg.text(
            text=index,
            insert=invert_y(rect.centre()),
        ))

    for elbow in elbows.elbows.values():
        for index, point in enumerate(elbow):
            dwg.add(dwg.circle(
                center=invert_y(point),
                fill="red",
                stroke="brown",
                stroke_width=10
            ))
            dwg.add(dwg.text(
                text=index,
                insert=invert_y(point),
                font_size="20px",
                font_weight="bold",
                fill="blue",
            ))

    for point in entities:
        dwg.add(dwg.circle(
            center=invert_y(point),
            fill="green",
            stroke="green",
            stroke_width=15
        ))


def draw_walls(dwg: svgwrite.Drawing, elbows: ElbowMaker):
    """Draw the walls around the paths"""
    smooth_line_calc = smoothing.smooth_line(smoothing=0.2, flip_y_height=400)
    connected, stubs = elbows.connected_elbows()
    dwg.add(dwg.path(
        d=smooth_line_calc(connected),
        fill="#f7faff",
        stroke="#000000",
        stroke_width=6
    ))
    for stub in stubs:
        dwg.add(dwg.path(
            d=smooth_line_calc(stub),
            fill="#f7faff",
            stroke="#000000",
            stroke_width=6
        ))


def load_configs(grid: Grid, exit_configs: typing.List[exit_config.ExitConfig]
                 ) -> typing.Dict[Dir, exit.Exit]:
    exits = {}
    for config in exit_configs:
        if config.direction == Dir.UP:
            exits[config.direction] = exit.Exit(
                Point(x=config.edge_position, y=grid.height - 1),
                is_blocked=config.is_blocked
            )
        if config.direction == Dir.DOWN:
            exits[config.direction] = exit.Exit(
                Point(x=config.edge_position, y=0),
                is_blocked=config.is_blocked
            )
        if config.direction == Dir.LEFT:
            exits[config.direction] = exit.Exit(
                Point(x=0, y=config.edge_position),
                is_blocked=config.is_blocked
            )
        if config.direction == Dir.RIGHT:
            exits[config.direction] = exit.Exit(
                Point(x=grid.width - 1, y=config.edge_position),
                is_blocked=config.is_blocked
            )

    return exits


def render_tile(exit_configs: typing.List[exit_config.ExitConfig]):
    tile_ = tile.Tile(width=600, height=400)
    grid = Grid(tile=tile_)

    exits = load_configs(grid, exit_configs)
    path = Path(grid.width, grid.height, exits=exits)

    elbows = ElbowMaker(grid, path)

    # Valid positions for entities (e.g. stairs)
    entities = [p * 100 for p in path.filled if (p.x > 0 and p.x < 6 and p.y > 0 and p.y < 4)]

    filename = 'tunnel.svg'

    dwg = svgwrite.Drawing(
        profile='tiny',
        filename=settings.TILE_OUTPUT_DIR + filename,
        size=(tile_.width, tile_.height)
    )
    draw_walls(dwg, elbows)
    # draw_debug(dwg, path, grid, elbows, entities)
    dwg.save()

    return settings.TILE_OUTPUT_DIR, entities, filename


if __name__ == '__main__':
    exit_configs = [
        exit_config.ExitConfig(Dir.UP, 4, False),
        exit_config.ExitConfig(Dir.DOWN, 4, True),
        exit_config.ExitConfig(Dir.LEFT, 1, False),
        exit_config.ExitConfig(Dir.RIGHT, 1, False),
    ]
    render_tile(exit_configs)

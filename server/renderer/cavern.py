import os
import sys
import random
import typing

import svgwrite
from scour import scour

package = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(package))

from common import settings
from common.point import Point
from common.enum import Direction as Dir
from renderer.common import exit, exit_config, smoothing, tile


class CavernShape:
    """Rectangle-like shape, with wobbly sides.

    :param origin: The lower-left `Point` of the shape.
    :param width: Width in `Tile` coordinates.
    :param height: Height in `Tile` coordinates.
    :param spacing: Spacing between `Point`s along each side.
    :param wobbliness: Parameter to adjust how wobbly the sides should be.
    :param exits: Mapping between `Direction`s and `Exit`s.
    where each `Exit` position is in `Tile` coordinates.
    :param exit_width: Width of the exits in `Tile` coordinates.

    """
    def __init__(self, origin: Point, width: int, height: int, spacing: int,
                 wobbliness: int, exits: typing.Dict[Dir, exit.Exit], exit_width: int):
        self.origin = origin
        self.width = width
        self.height = height
        self.spacing = spacing
        self.wobbliness = wobbliness
        self.exits = exits
        self.exit_width = exit_width

        self.runge_offset = 30
        self.offsets = self._calculate_offsets()
        self.sides = self._calculate_sides()
        self.perimeter = self._calculate_perimeter()
        self.stubs = self._calculate_stubs()

    def _calculate_offsets(self) -> typing.Dict[Dir, Point]:
        offsets = {}

        for dir_ in Dir.all_nesw():
            amount = random.randint(20, 40)
            exit_ = self.exits[dir_]
            if exit_.is_blocked:
                if dir_ in {Dir.UP, Dir.RIGHT}:
                    offsets[dir_] = Point.direction_vector(dir_) * amount
                else:
                    offsets[dir_] = Point.direction_vector(Dir.mirror_of(dir_)) * amount
            else:
                offsets[dir_] = Point(0, 0)

        return offsets

    def _calculate_sides(self) -> typing.Dict[Dir, typing.List[Point]]:
        sides = {
            Dir.UP: [],
            Dir.RIGHT: [],
            Dir.DOWN: [],
            Dir.LEFT: [],
        }

        offset = self.offsets[Dir.UP]
        sides[Dir.UP] += self._create_points(
            start=Point(self.origin.x, self.origin.y + self.height - offset.y),
            end=Point(self.origin.x + self.width, self.origin.y + self.height - offset.y),
            increment=Point(self.spacing, 0)
        )

        offset = self.offsets[Dir.RIGHT]
        sides[Dir.RIGHT] += self._create_points(
            start=Point(self.origin.x + self.width - offset.x, self.origin.y),
            end=Point(self.origin.x + self.width - offset.x, self.origin.y + self.height),
            increment=Point(0, self.spacing)
        )
        sides[Dir.RIGHT].reverse()

        offset = self.offsets[Dir.DOWN]
        sides[Dir.DOWN] += self._create_points(
            start=Point(self.origin.x, self.origin.y + offset.y),
            end=Point(self.origin.x + self.width, self.origin.y + offset.y),
            increment=Point(self.spacing, 0)
        )
        sides[Dir.DOWN].reverse()

        offset = self.offsets[Dir.LEFT]
        sides[Dir.LEFT] += self._create_points(
            start=Point(self.origin.x + offset.x, self.origin.y),
            end=Point(self.origin.x + offset.x, self.origin.y + self.height),
            increment=Point(0, self.spacing)
        )

        return sides

    def _create_points(self, start: Point, end: Point,
                       increment: Point) -> typing.List[Point]:
        dist = start
        new_points = []

        while dist.x <= end.x and dist.y <= end.y:
            new_point = Point(dist.x, dist.y)

            if increment.x == 0:
                new_point.x += random.randint(-self.wobbliness, self.wobbliness)

            if increment.y == 0:
                new_point.y += random.randint(-self.wobbliness, self.wobbliness)

            new_points.append(new_point)
            dist += increment

        # Remove corners
        return new_points[1:-1]

    def _calculate_perimeter(self) -> typing.List[Point]:
        perimeter = []

        for direction in [Dir.UP, Dir.RIGHT, Dir.DOWN, Dir.LEFT]:
            elbow = self._calculate_elbow(direction, Dir.clockwise_of(direction))
            perimeter += elbow

        # Ensure path wraps around on itself and does not leave a gap
        perimeter.append(perimeter[0])

        return perimeter

    def _calculate_elbow(self, start_dir: Dir, end_dir: Dir):
        elbow = []

        exit_ = self.exits[start_dir]
        start_dir_vector = Point.direction_vector(start_dir)

        exit_point = Point(
            exit_.point.x + (start_dir_vector.y * self.exit_width / 2),
            exit_.point.y - (start_dir_vector.x * self.exit_width / 2)
        )
        runge_point = exit_point.translate(start_dir, self.runge_offset)

        side = self.sides[start_dir]
        if not exit_.is_blocked:
            # Find and align nearest side point
            if start_dir in {Dir.UP, Dir.DOWN}:
                nearest_side_point = min(side, key=lambda sp: abs(sp.x - exit_point.x))
                index = side.index(nearest_side_point)
                side[index] = Point(exit_point.x, side[index].y)
            else:
                nearest_side_point = min(side, key=lambda sp: abs(sp.y - exit_point.y))
                index = side.index(nearest_side_point)
                side[index] = Point(side[index].x, exit_point.y)

            # TODO: Mark runge point index.
            elbow += [runge_point, exit_point]

            for side_point in side[index:]:
                elbow.append(side_point)

        ############################

        exit_ = self.exits[end_dir]
        end_dir_vector = Point.direction_vector(end_dir)

        exit_point = Point(
            exit_.point.x - (end_dir_vector.y * self.exit_width / 2),
            exit_.point.y + (end_dir_vector.x * self.exit_width / 2)
        )
        runge_point = exit_point.translate(end_dir, self.runge_offset)

        # Find and align nearest side point
        side = self.sides[end_dir]
        if not exit_.is_blocked:
            if end_dir in {Dir.UP, Dir.DOWN}:
                nearest_side_point = min(side, key=lambda sp: abs(sp.x - exit_point.x))
                index = side.index(nearest_side_point)
                side[index] = Point(exit_point.x, side[index].y)
            else:
                nearest_side_point = min(side, key=lambda sp: abs(sp.y - exit_point.y))
                index = side.index(nearest_side_point)
                side[index] = Point(side[index].x, exit_point.y)

            for side_point in side[:index + 1]:
                elbow.append(side_point)

            # TODO: Mark runge point index.
            elbow += [exit_point, runge_point]
        else:
            for side_point in side:
                elbow.append(side_point)

        return elbow

    def _calculate_stubs(self) -> typing.Dict[Dir, typing.List[Point]]:
        # For each side, create a stub with length up to an amount determined by the
        # offset for that side.
        stubs = {}

        for dir_ in Dir.all_nesw():
            offset = self.offsets[dir_]
            if offset == Point(0, 0):
                continue

            exit_ = self.exits[dir_].point
            start_point = exit_.translate(Dir.clockwise_of(dir_), self.exit_width / 2)
            stub = [start_point.translate(dir_, self.runge_offset)]

            # TODO: Add points between by integrating with utils.points_between
            length = abs(offset.x) if offset.x else abs(offset.y)
            width = self.exit_width

            stub.append(start_point.translate(Dir.mirror_of(dir_), length))
            stub.append(stub[-1].translate(Dir.anticlockwise_of(dir_), width))
            stub.append(stub[-1].translate(dir_, width + self.runge_offset))

            stubs[dir_] = stub

        return stubs


def invert_y(point: Point) -> Point:
    # TODO: Build wrapper around dwg to invert automatically and handle boilerplate
    return point.x, 400 - point.y


def draw_debug(dwg: svgwrite.Drawing, cavern_shape: CavernShape, entities):
    for dir_ in cavern_shape.sides:
        for index, point in enumerate(cavern_shape.sides[dir_]):
            dwg.add(dwg.circle(
                center=invert_y(point),
                fill="red",
                stroke="brown",
                stroke_width=12
            ))
            dwg.add(dwg.text(
                insert=invert_y(point),
                font_size="30px",
                font_weight="bold",
                fill="blue",
                text=index
            ))
        dwg.add(dwg.circle(
            center=invert_y(cavern_shape.exits[dir_].point),
            fill="red",
            stroke="brown",
            stroke_width=12
        ))

    for dir_ in Dir.all_nesw():
        if not cavern_shape.stubs.get(dir_):
            continue

        for index, point in enumerate(cavern_shape.stubs[dir_]):
            dwg.add(dwg.circle(
                center=invert_y(point),
                fill="red",
                stroke="brown",
                stroke_width=12
            ))
            dwg.add(dwg.text(
                insert=invert_y(point),
                font_size="30px",
                font_weight="bold",
                fill="blue",
                text=index
            ))

    for point in entities:
        dwg.add(dwg.circle(
            center=invert_y(point),
            fill="green",
            stroke="green",
            stroke_width=15
        ))


def draw_walls(dwg: svgwrite.Drawing, cavern_shape: CavernShape):
    smooth_line_calc = smoothing.smooth_line(smoothing=0.2, flip_y_height=400)

    dwg.add(dwg.path(
        d=smooth_line_calc(cavern_shape.perimeter),
        fill="#f7faff",
        stroke="#000000",
        stroke_width=6
    ))

    for dir_ in Dir.all_nesw():
        if not cavern_shape.stubs.get(dir_):
            continue

        dwg.add(dwg.path(
            d=smooth_line_calc(cavern_shape.stubs[dir_]),
            fill="#f7faff",
            stroke="#000000",
            stroke_width=6
        ))


def grid_to_tile(val: int) -> int:
    if val == 0:
        return val + 50
    if val > 0:
        return val * 100
    raise ValueError(f"invalid grid position: {val}")


def load_configs(tile: tile.Tile, exit_configs: typing.List[exit_config.ExitConfig]
                 ) -> typing.Dict[Dir, exit.Exit]:
    exits = {}
    for config in exit_configs:
        if config.direction == Dir.UP:
            exits[config.direction] = exit.Exit(
                Point(x=grid_to_tile(config.edge_position), y=tile.height - 1),
                is_blocked=config.is_blocked
            )
        if config.direction == Dir.DOWN:
            exits[config.direction] = exit.Exit(
                Point(x=grid_to_tile(config.edge_position), y=0),
                is_blocked=config.is_blocked
            )
        if config.direction == Dir.LEFT:
            exits[config.direction] = exit.Exit(
                Point(x=0, y=grid_to_tile(config.edge_position)),
                is_blocked=config.is_blocked
            )
        if config.direction == Dir.RIGHT:
            exits[config.direction] = exit.Exit(
                Point(x=tile.width - 1, y=grid_to_tile(config.edge_position)),
                is_blocked=config.is_blocked
            )

    return exits


def scour_tile(name):
    input_path = settings.TILE_OUTPUT_DIR + name + '.svg'
    output_path = settings.TILE_OUTPUT_DIR + name + '_scoured.svg'
    options = scour.parse_args(args=[input_path, output_path])
    scour.start(options, *scour.getInOut(options))
    return name + '_scoured.svg'


def render_tile(exit_configs: typing.List[exit_config.ExitConfig]):
    tile_ = tile.Tile(width=600, height=400)

    margin = 50
    exits = load_configs(tile_, exit_configs)
    cavern_shape = CavernShape(
        origin=Point(margin, margin),
        width=tile_.width - (2 * margin),
        height=tile_.height - (2 * margin),
        spacing=45,  # TODO: 25 for deeper floors
        wobbliness=25,
        exits=exits,
        exit_width=100,
    )

    # Valid positions for entities (e.g. stairs)
    entities = [Point(220, 150), Point(220, 250), Point(380, 150), Point(380, 250)]

    exit_pos = [
        Point(
            e.point.x * 100 + (0 if e.point.y else 50),
            e.point.y * 100 + (0 if e.point.x else 50)
        )
        for e in exits.values()
    ]

    name = 'cavern'
    dwg = svgwrite.Drawing(
        profile='tiny',
        filename=settings.TILE_OUTPUT_DIR + name + '.svg',
        size=(tile_.width, tile_.height)
    )
    draw_walls(dwg, cavern_shape)
    # draw_debug(dwg, cavern_shape, entities)
    dwg.save()

    filename = scour_tile(name)

    return settings.TILE_OUTPUT_DIR, entities, exits_pos, filename


if __name__ == '__main__':
    exit_configs = [
        exit_config.ExitConfig(Dir.UP, 4, False),
        exit_config.ExitConfig(Dir.DOWN, 1, False),
        exit_config.ExitConfig(Dir.LEFT, 3, True),
        exit_config.ExitConfig(Dir.RIGHT, 3, True),
    ]
    render_tile(exit_configs)

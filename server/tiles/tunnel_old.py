import enum
import math
import random
from typing import List

import svgwrite

import smoothing

TILE_HEIGHT = 400
TILE_WIDTH = 600
DEBUG = False
smooth_line_calc = smoothing.smooth_line(smoothing=0.2, flip_y_height=TILE_HEIGHT)


class Side(enum.Enum):
    # Note that Python enum ordering matters for iteration
    WEST = 'west'
    NORTH = 'north'
    EAST = 'east'
    SOUTH = 'south'


class ExitPos(enum.Enum):
    """Represents the position of an exit, as evaluated left-to-right on north and south
    sides of a tile, and bottom-to-top on west and east sides of a tile.

    """
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

    @staticmethod
    def random():
        return random.choice(list(ExitPos))


class ExitConf:
    """Configuration object for a `TileLayout`.

    """
    def __init__(self, side: Side, enabled: bool, pos: ExitPos):
        self.side = side
        self.enabled = enabled
        self.pos = pos


class Elbow:
    """Comprises a start and end exit point, an intersection point, and any number of
    intermediary points.

    """
    intermediaries: List[int]

    def __init__(self, start, end, intersection):
        self.start = start
        self.end = end
        self.intersection = intersection
        self.intermediaries1 = []
        self.intermediaries2 = []

    def get_all_points(self):
        return [
            *self.intermediaries1,
            *self.intermediaries2
        ]


class TileLayout:
    EXIT_WIDTH = 45

    exits = []
    exit_points = []
    intersections = []

    elbows = []

    def __init__(self, conf: ExitConf):
        for exit in conf:
            # Calculate actual distance
            exit.mid = self._calculate_mid(exit.side, exit.pos)
            self.exits.append(exit)

    @staticmethod
    def _calculate_mid(side: Side, position: 'ExitPosition'):
        if side in {Side.WEST, Side.EAST}:
            if position == ExitPos.LOW:
                return math.floor(TILE_HEIGHT / 6)
            if position == ExitPos.MEDIUM:
                return math.floor(TILE_HEIGHT / 2)
            if position == ExitPos.HIGH:
                return math.floor(TILE_HEIGHT / 6 * 5)
        if side in {Side.NORTH, Side.SOUTH}:
            if position == ExitPos.LOW:
                return math.floor(TILE_WIDTH / 6)
            if position == ExitPos.MEDIUM:
                return math.floor(TILE_WIDTH / 2)
            if position == ExitPos.HIGH:
                return math.floor(TILE_WIDTH / 6 * 5)

    def calculate_exit_points(self):
        """Go clockwise around the tile, calculating the coordinates of each exit point.

        """
        for exit in self.exits:
            if exit.side == Side.WEST:
                self.exit_points.append(([0, exit.mid - self.EXIT_WIDTH], exit.side))
                self.exit_points.append(([0, exit.mid + self.EXIT_WIDTH], exit.side))
            elif exit.side == Side.NORTH:
                self.exit_points.append(([exit.mid - self.EXIT_WIDTH, TILE_HEIGHT], exit.side))
                self.exit_points.append(([exit.mid + self.EXIT_WIDTH, TILE_HEIGHT], exit.side))
            elif exit.side == Side.EAST:
                self.exit_points.append(([TILE_WIDTH, exit.mid + self.EXIT_WIDTH], exit.side))
                self.exit_points.append(([TILE_WIDTH, exit.mid - self.EXIT_WIDTH], exit.side))
            elif exit.side == Side.SOUTH:
                self.exit_points.append(([exit.mid + self.EXIT_WIDTH, 0], exit.side))
                self.exit_points.append(([exit.mid - self.EXIT_WIDTH, 0], exit.side))

    def calculate_elbows(self):
        # Start at top-left and continue round to bottom-right
        # TODO: Generic so can start at any exit point and work clockwise around
        for i in range(1, len(self.exit_points), 2):
            # TODO: Handle case where start / end point are disabled.
            start_point, start_side = self.exit_points[i % len(self.exit_points)]
            end_point, end_side = self.exit_points[(i + 1) % len(self.exit_points)]

            start_inward_line = self._calc_inward_line(start_point, start_side)
            end_inward_line = self._calc_inward_line(end_point, end_side)

            # Returns an intersection point, if it exists
            intersection_point = self._calc_intersection(start_inward_line, end_inward_line)

            # import pdb; pdb.set_trace()
            self.intersections.append(intersection_point)

            # Create new elbow
            elbow = Elbow(start=start_point, end=end_point, intersection=intersection_point)

            # Draw random points between start point --> intersection point
            points = self._dots_between_points(start_point, intersection_point)
            elbow.intermediaries1 += points

            # Draw random points between intersection point --> end point
            points = self._dots_between_points(intersection_point, end_point, to_edge=True)
            elbow.intermediaries2 += points

            self.elbows.append(elbow)

    def _dots_between_points(self, p1, p2, to_edge=False):
        x_mult, y_mult, dist = self._mults(p1, p2)
        allowed_variation = 10
        spacing = 30
        points = []

        i = -60 if not to_edge else spacing
        end = dist + spacing if to_edge else dist
        while i < end:
            variation = random.randint(-allowed_variation, allowed_variation)
            point = [
                p1[0] + (x_mult * i) + (variation if y_mult != 0 else 0),
                p1[1] + (y_mult * i) + (variation if x_mult != 0 else 0)
            ]
            points.append(point)

            i += spacing

        return points

    def _mults(self, p1, p2):
        if p1[0] == p2[0]:
            x_mult = 0
            y_mult = self._int_sign(p2[1] - p1[1])
            dist = abs(p1[1] - p2[1])
        elif p1[1] == p2[1]:
            x_mult = self._int_sign(p2[0] - p1[0])
            y_mult = 0
            dist = abs(p1[0] - p2[0])
        else:
            raise ValueError('p1 and p2 should share one coordinate')

        return x_mult, y_mult, dist

    def _int_sign(self, x):
        return bool(x > 0) - bool(x < 0)

    def _first_leg_lim(self, side, intersection):
        if side in {Side.WEST, Side.EAST}:
            return intersection[0]
        else:
            return intersection[1]

    def _calc_inward_line(self, point, side):
        """Returns a line extending from the point inwards to the other side of the tile.

        """
        p1 = [point[0], point[1]]

        if side == Side.WEST:
            p2 = [point[0] + TILE_WIDTH, point[1]]
        if side == Side.NORTH:
            p2 = [point[0], point[1] - TILE_WIDTH]
        if side == Side.EAST:
            p2 = [point[0] - TILE_WIDTH, point[1]]
        if side == Side.SOUTH:
            p2 = [point[0], point[1] + TILE_WIDTH]

        return self._calc_line(p1, p2)

    def _calc_line(self, p1, p2):
        a = p1[1] - p2[1]
        b = p2[0] - p1[0]
        c = p1[0] * p2[1] - p2[0] * p1[1]
        return a, b, -c

    def _calc_intersection(self, l1, l2):
        """Returns an intersection point, if one exists.

        """
        d = l1[0] * l2[1] - l1[1] * l2[0]
        dx = l1[2] * l2[1] - l1[1] * l2[2]
        dy = l1[0] * l2[2] - l1[2] * l2[0]

        if d == 0:
            return False

        x = dx / d
        y = dy / d
        return [x, y]

    def calc_elbows(self):
        for intersection in self.intersections:
            pass


def draw_tunnel_debug(dwg, tile_layout):
    for elbow in tile_layout.elbows:
        points = elbow.get_all_points()
        for point in points:
            dwg.add(dwg.circle(
                center=(invert_y(point)),
                fill="red",
                stroke="brown",
                stroke_width=10
            ))
        for exit in [elbow.start, elbow.end]:
            dwg.add(dwg.circle(
                center=(invert_y(exit)),
                fill="none",
                stroke="blue",
                stroke_width=12
            ))
        dwg.add(dwg.circle(
            center=(invert_y(elbow.intersection)),
            fill="none",
            stroke="red",
            stroke_width=12
        ))


def draw_tunnel(dwg):
    exits = [
        ExitConf(side=Side.WEST, enabled=True, pos=ExitPos.random()),
        ExitConf(side=Side.NORTH, enabled=True, pos=ExitPos.random()),
        ExitConf(side=Side.EAST, enabled=True, pos=ExitPos.random()),
        ExitConf(side=Side.SOUTH, enabled=True, pos=ExitPos.random()),
    ]

    tile_layout = TileLayout(exits)
    tile_layout.calculate_exit_points()
    tile_layout.calculate_elbows()

    if DEBUG:
        draw_tunnel_debug(dwg, tile_layout)

    # Draw points
    for elbow in tile_layout.elbows:
        points = elbow.get_all_points()
        dwg.add(dwg.path(
            d=smooth_line_calc(points),
            fill="none",
            stroke="#000000",
            stroke_width=6
        ))

    dwg.save()


def invert_y(point):
    return point[0], TILE_HEIGHT - point[1]


def _draw_test_points(dwg):
    x = 0
    y = 250
    startY = 250

    x_dist = 30
    y_dist = 30
    y_dist_max = 30
    c = 0.6

    points = []

    while x <= TILE_WIDTH:
        points.append([x, y])

        # y = startY + c * (y_i-1 - startY) + err
        y = startY + c * (y - startY) + random.randint(-y_dist, y_dist)

        if y - startY > y_dist_max:
            y = startY + y_dist_max
        elif y - startY < -y_dist_max:
            y = startY - y_dist_max

        x += x_dist

    dwg.add(dwg.path(
        d=smooth_line_calc(points),
        fill="none",
        stroke="#000000",
        stroke_width=6
    ))

    for point in points:
        dwg.add(dwg.circle(
            center=(point),
            fill="red",
            stroke="brown",
            stroke_width=10
        ))

    dwg.save()


def main():
    dwg = svgwrite.Drawing('test.svg', size=(TILE_WIDTH, TILE_HEIGHT), profile='tiny')
    draw_tunnel(dwg)
    # _draw_test_points(dwg)


if __name__ == '__main__':
    main()

import random
import typing

from common.point import Point


def calculate_points_between(p1: Point, p2: Point, spacing: int,
                             wobbliness: int) -> typing.List[Point]:
    x_mult, y_mult, dist = _mults(p1, p2)
    # allowed_variation = 10
    # spacing = 30
    points = []

    i = spacing
    while i < dist:
        variation = random.randint(-wobbliness, wobbliness)
        point = Point(
            p1.x + (x_mult * i) + (variation if y_mult != 0 else 0),
            p1.y + (y_mult * i) + (variation if x_mult != 0 else 0)
        )
        points.append(point)

        i += spacing

    return points


def _mults(p1: Point, p2: Point) -> (float, float, float):
    if p1.x == p2.x:
        x_mult = 0
        y_mult = _int_sign(p2.y - p1.y)
        dist = abs(p1.y - p2.y)
    elif p1.y == p2.y:
        x_mult = _int_sign(p2.x - p1.x)
        y_mult = 0
        dist = abs(p1.x - p2.x)
    else:
        y_mult = 0
        dist = 0
        raise ValueError(f"p1 and p2 should share one coordinate: p1={p1}, p2={p2}")

    return x_mult, y_mult, dist


def _int_sign(x: int):
    return bool(x > 0) - bool(x < 0)

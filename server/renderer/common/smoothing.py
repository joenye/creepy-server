import math
from typing import Callable, Dict, List

from common.point import Point


# pylint: disable=invalid-name
def smooth_line(smoothing: float = 0.2, flip_y_height: int = None) -> Callable:
    control_point_calc = _control_point(_line, smoothing)
    bezier_command_calc = _bezier_command(control_point_calc)

    def fn(points: List[Point]):
        if flip_y_height:
            points = [Point(point.x, flip_y_height - point.y) for point in points]

        return _svg_path(points, bezier_command_calc)

    return fn


def _line(pointA: Point, pointB: Point) -> Dict[str, float]:
    """Calculates the properties of a given line.

    :param pointA:
    :type pointA: list
    :param pointB:
    :type pointB: list
    :returns: `dict` of { length: int, angle: int }

    """
    lengthX = pointB.x - pointA.x
    lengthY = pointB.y - pointA.y

    return {
        "length": math.sqrt(lengthX ** 2 + lengthY ** 2),
        "angle": math.atan2(lengthY, lengthX),
    }


def _control_point(
    line_calc: Callable[[Point, Point], dict], smooth: float
) -> Callable:
    """Creates a function to calculate the position of a control point.

    :param line_calc: `Callable` returned by the `line` function.
    :param smooth: Smoothness parameter.
    :returns: `Callable` to calculate the position of a control point.

    """

    def fn(
        current: Point, previous: Point, next_: Point, reverse: bool = False
    ) -> Point:
        """Calculates the position of a control point.

        :param current: Current coordinates.
        :param previous: Previous coordinates.
        :param next_: Next coordinates.
        :param reverse: Whether direction should be reversed.
        :returns: Control point coordinate.

        """
        # Replace 'previous' and 'next' with 'current' if they don't exist (i.e. when
        # current is either the first or last point in the input array)
        previous = previous if previous else current
        next_ = next_ if next_ else current

        line_props = line_calc(previous, next_)

        # If is the end-control-point, add pi to the angle to go backward
        angle = line_props["angle"] + (math.pi if reverse else 0)
        length = line_props["length"] * smooth

        # The control point position is relative to the current point
        x = current.x + math.cos(angle) * length
        y = current.y + math.sin(angle) * length

        return Point(x, y)

    return fn


def _bezier_command(control_point_calc: Callable[[Point], Point]) -> Callable:
    """Creates a function to calculate a bezier curve command.

    :param control_point_calc: `Callable` returned by the `control_point` function.
    :returns: `Callable` to calculate a bezier curve command.

    """

    def fn(point: Point, i: int, list_: List[Point]) -> str:
        """Calculates a bezier curve command.

        :param point: Current point coordinates.
        :param i: Index of a point in the given coordinate list, 'list_'.
        :param list_: Complete list of points coordinates.
        :return: Cubic bezier command, as a string: 'C x2,y2 x1,y1 x,y'.

        """
        # Start control point
        cp = control_point_calc(list_[i - 1], list_[i - 2], point)

        # End control point
        try:
            next_ = list_[i + 1]
        except IndexError:
            next_ = None

        cpe = control_point_calc(
            current=point, previous=list_[i - 1], next_=next_, reverse=True
        )

        return f"C {cp.x},{cp.y} {cpe.x},{cpe.y} {point.x},{point.y}"

    return fn


def _svg_path(
    points: List[Point], command: Callable[[Point, int, List[Point]], str]
) -> str:
    """Calculates the smoothed SVG path command.

    :param points: List of points coordinates.
    :param command: `Callable` returned by the `bezier_command` function.
    :return: SVG path command.

    """
    d_ = ""
    for i in range(len(points)):
        point = points[i]

        if not d_:
            d_ = f"M {point.x},{point.y}"
        else:
            seg_cmd = command(point, i, points)
            d_ = f"{d_} {seg_cmd}"

    return d_

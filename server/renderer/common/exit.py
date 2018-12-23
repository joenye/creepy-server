import typing

from common.point import Point


class Exit(typing.NamedTuple):
    point: Point
    is_blocked: bool

from common.enum import Direction


# pylint: disable=invalid-name
class Point:
    """Container for coordinates, as well as helper methods.

    :param x: x-coordinate.
    :param y: y-coordinate.
    :param z: z-coordinate, which defaults to None to indicate a 2D point.

    """

    def __init__(self, x: int, y: int, z: int = None) -> None:
        self.x = x
        self.y = y
        self.z = z

    def translate(self, direction: Direction, amount: int = 1):
        if direction == Direction.UP:
            return Point(self.x, self.y + amount, self.z)
        if direction == Direction.RIGHT:
            return Point(self.x + amount, self.y, self.z)
        if direction == Direction.DOWN:
            return Point(self.x, self.y - amount, self.z)
        if direction == Direction.LEFT:
            return Point(self.x - amount, self.y, self.z)
        if direction == Direction.ABOVE:
            return Point(self.x, self.y, self.z - amount)
        if direction == Direction.BELOW:
            return Point(self.x, self.y, self.z + amount)
        raise ValueError(f"{direction} is not a supported {Direction.__name__}")

    @classmethod
    def distance_between(cls, p1, p2) -> int:
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    @classmethod
    def direction_vector(cls, direction: Direction):
        if direction == Direction.UP:
            return Point(0, 1)
        if direction == Direction.RIGHT:
            return Point(1, 0)
        if direction == Direction.DOWN:
            return Point(0, -1)
        if direction == Direction.LEFT:
            return Point(-1, 0)
        if direction == Direction.ABOVE:
            return Point(0, 0, -1)
        if direction == Direction.BELOW:
            return Point(0, 0, 1)
        raise ValueError(f"{direction} is not a supported {Direction.__name__}")

    def copy(self):
        return type(self)(x=self.x, y=self.y)

    def serialize(self, strip_z=False) -> str:
        if self.z is not None and strip_z is False:
            return f"x={self.x},y={self.y},z={self.z}"
        return f"x={self.x},y={self.y}"

    @classmethod
    def deserialize(cls, serialized: str):
        try:
            x, y, z = [int(part[2:]) for part in serialized.split(",")]
        except ValueError:
            x, y = [int(part[2:]) for part in serialized.split(",")]
            z = None

        return Point(x, y, z)

    def __add__(self, p2):
        if isinstance(p2, int):
            return Point(self.x + p2, self.y + p2, self.z)
        if isinstance(p2, Point):
            return Point(self.x + p2.x, self.y + p2.y, self.z)

        raise TypeError(f"addition between Point and {type(p2)} is not supported")

    def __mul__(self, p2):
        if isinstance(p2, int):
            return Point(self.x * p2, self.y * p2, self.z)
        if isinstance(p2, Point):
            return Point(self.x * p2.x, self.y * p2.y, self.z)

        raise TypeError(f"multiplication between Point and {type(p2)} is not supported")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __repr__(self):
        if self.z is not None:
            return f"(x={self.x}, y={self.y}, z={self.z})"
        return f"(x={self.x}, y={self.y})"

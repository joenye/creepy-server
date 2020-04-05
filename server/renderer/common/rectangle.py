from common.point import Point


class Rectangle:
    """Simple rectangle, with helper methods.

    """

    # pylint: disable=invalid-name
    def __init__(self, bl: Point, br: Point, tl: Point, tr: Point) -> None:
        self.bl = bl
        self.br = br
        self.tl = tl
        self.tr = tr

    def translate(self, x: int, y: int) -> None:
        self.bl = Point(self.bl.x + x, self.bl.y + y)
        self.br = Point(self.br.x + x, self.br.y + y)
        self.tl = Point(self.tl.x + x, self.tl.y + y)
        self.tr = Point(self.tr.x + x, self.tr.y + y)

    def centre(self) -> Point:
        return Point((self.tl.x + self.tr.x) / 2, (self.tl.y + self.bl.y) / 2)

    def width(self) -> int:
        return self.tr.x - self.tl.x

    def height(self) -> int:
        return self.tl.y - self.bl.y

    def __eq__(self, other) -> bool:
        return (
            self.bl == other.bl
            and self.br == other.br
            and self.tl == other.tl
            and self.tr == other.tr
        )

    def __repr__(self) -> str:
        return f"Rect: (bl={self.bl}, br={self.br}, tl={self.tl}, tr={self.tr})"

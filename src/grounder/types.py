from dataclasses import dataclass


@dataclass
class BBox:
    x1: int
    y1: int
    x2: int
    y2: int

    def __post_init(self):
        if self.x2 < self.x1 or self.y2 < self.y1:
            raise ValueError(f"Invalid bbox: x2<x1 or y2<y1 in {self}")

    @property
    def center(self) -> tuple[int, int]:
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def area(self) -> int:
        return self.width * self.height

    def translate(self, dx: int, dy: int) -> BBox:
        return BBox(
            self.x1 + dx,
            self.y1 + dy,
            self.x2 + dx,
            self.y2 + dy,
        )


@dataclass
class Viewport:
    x: int
    y: int
    width: int
    height: int

    def to_screen(self, local_box: BBox) -> BBox:
        return local_box.translate(self.x, self.y)

    @classmethod
    def full(cls, width: int, height: int) -> Viewport:
        return cls(0, 0, width, height)

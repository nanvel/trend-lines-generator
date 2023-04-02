import datetime
import math
from dataclasses import dataclass
from functools import cached_property
from typing import Union

from .side import Side
from .time import Time


@dataclass(frozen=True)
class Line:
    side: Side
    a: float
    b: float
    width: float
    x_start: int

    def get_y(self, x: Union[int, datetime.datetime]):
        if isinstance(x, datetime.datetime):
            x = Time.from_datetime(x)
        return self.a * x + self.b

    @property
    def is_horizontal(self) -> bool:
        return not self.a

    def __hash__(self):
        return hash((self.side, self.a, self.b))


class LineCandidate:
    def __init__(
        self,
        side: Side,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ):
        self.side = side
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.a = (y2 - y1) / (x2 - x1)
        self.b = y2 - self.a * x2

        self.pivots = []
        self.pivots_opposite = []
        self.quality: float = 0

    @cached_property
    def angle_rad(self):
        return math.atan((self.y2 - self.y1) / (self.x2 - self.x1))

    @property
    def angle(self):
        return self.angle_rad * 180 / math.pi

    @property
    def is_horizontal(self) -> bool:
        return self.a == 0

    def get_y(self, x: int) -> float:
        return self.a * x + self.b

    def get_x(self, y: float) -> float:
        if self.a == 0:
            return self.x2
        return (y - self.b) / self.a

    def get_distance(self, x: int, y: float):
        if self.angle_rad == 0:
            return abs(y - self.get_y(x))
        return (x - self.get_x(y)) * math.sin(self.angle_rad)

    def __str__(self):
        return f"Line[{int(self.x1)},{self.y1:.2f} {int(self.x2)},{self.y2:.2f} a{int(self.angle)}]"

import datetime
import math
from dataclasses import dataclass
from functools import cached_property
from typing import Union

from .side import Side
from .time import Time


@dataclass(frozen=True)
class ALine:
    side: Side
    a: float
    b: float

    def get_y(self, x: Union[int, datetime.datetime]):
        if isinstance(x, datetime.datetime):
            x = Time.from_datetime(x)
        return self.a * x + self.b


class ALineCandidate:
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

        self.pivots = set()
        self.pivots_extra = set()
        self.distance: float = 0
        self.distance_extra: float = 0

    @cached_property
    def angle_rad(self):
        return math.atan((self.y2 - self.y1) / (self.x2 - self.x1))

    @property
    def angle(self):
        return self.angle_rad * 180 / math.pi

    def get_y(self, x: int) -> float:
        return self.a * x + self.b

    def get_x(self, y: float) -> float:
        return (y - self.b) / self.a

    def get_distance(self, x: int, y: float):
        return (x - self.get_x(y)) * math.sin(self.angle_rad)

    def __str__(self):
        return f"ALine[{int(self.x1)},{self.y1:.2f} {int(self.x2)},{self.y2:.2f} a{int(self.angle)}]"

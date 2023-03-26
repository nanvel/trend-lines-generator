from functools import lru_cache
from typing import List

from numpy import NaN
from pandas import DataFrame

from .side import Side
from .time import Time


class Board:
    def __init__(
        self,
        df: DataFrame,
        x_start: float,
        x_step: float,
        y_start: float,
        y_step: float,
        x_is_datetime: bool,
    ):
        self.df = df
        self.x_start = x_start
        self.x_step = x_step
        self.y_start = y_start
        self.y_step = y_step
        self.x_is_datetime = x_is_datetime

    @property
    def size(self) -> int:
        return len(self.df.index)

    def get_y(self, x, side: Side) -> float:
        return self.df.loc[x, side]

    def translate(self, x, y):
        x = x * self.x_step + self.x_start
        if self.x_is_datetime:
            x = Time(x).to_datetime()
        return x, y * self.y_step + self.y_start

    @lru_cache
    def get_pivots(self, side: Side) -> List[int]:
        repetitive = self.df[self.df[side].shift() == self.df[side]].index

        df = self.df.drop(repetitive)

        df[f"pivot_{side}"] = (
            df[side]
            .rolling(3, center=True)
            .apply(getattr(self, f"_is_{side}"))
            .replace(0, NaN)
        )

        pivots = list(df[df[f"pivot_{side}"].notnull()].index)[:-1]

        to_remove = set()
        for p in pivots:
            around = []
            for i in (p - 3, p - 2, p + 2, p + 3):
                if i < 0 or i >= self.size:
                    continue
                around.append(self.get_y(i, side=side))

            current = self.get_y(p, side=side)
            if side == Side.LOW and min(around) < current:
                to_remove.add(p)
            elif side == Side.HIGH and max(around) > current:
                to_remove.add(p)

        pivots = [p for p in pivots if p not in to_remove]

        return pivots

    @staticmethod
    def _is_high(values) -> bool:
        return values.iat[1] > values.iat[0] and values.iat[1] > values.iat[2]

    @staticmethod
    def _is_low(values) -> bool:
        return values.iat[1] < values.iat[0] and values.iat[1] < values.iat[2]

import math
from statistics import median
from typing import List

import numpy as np

from tlines.models import ALine, ALineCandidate, Board, Side, Time


class GenerateALines:
    def __init__(
        self,
        board: Board,
        min_pivot_distance: float = 0.1,
    ):
        self.board = board
        self.min_pivot_distance = min_pivot_distance

        # median distance between points
        self.band = max(
            np.sqrt(1 + np.square(board.df[Side.LOW].diff())).median(),
            np.sqrt(1 + np.square(board.df[Side.HIGH].diff())).median(),
        )

        self.pivots = {
            Side.LOW: [
                (p, self.board.get_y(p, side=Side.LOW))
                for p in board.get_pivots(side=Side.LOW)
            ],
            Side.HIGH: [
                (p, self.board.get_y(p, side=Side.HIGH))
                for p in board.get_pivots(side=Side.HIGH)
            ],
        }

    def __call__(self):
        for side in [Side.LOW, Side.HIGH]:
            lines = self._cluster(
                lines=list(
                    self._filter_lines(
                        lines=self._suggest_lines(
                            pivots=[p for p, _ in self.pivots[side]],
                            side=side,
                        ),
                        side=side,
                    )
                )
            )

            for line in lines:
                x1, y1 = self.board.translate(line.x1, line.y1)
                x2, y2 = self.board.translate(line.x2, line.y2)

                x1 = Time.from_datetime(x1)
                x2 = Time.from_datetime(x2)

                a = (y2 - y1) / (x2 - x1)
                b = y2 - a * x2

                yield ALine(
                    side=side,
                    a=a,
                    b=b,
                )

    def _filter_lines(self, lines, side: Side):
        seen = set()
        for line in lines:
            key = (line.a, line.b)
            if key in seen:
                continue

            for x, y in self.pivots[side]:
                if abs(y - line.get_y(x)) <= self.band:
                    line.pivots.add(x)
            if len(line.pivots) >= 3:
                for x, y in self.pivots[side.opposite(side)]:
                    if abs(y - line.get_y(x)) <= self.band:
                        line.pivots_extra.add(x)

                line.distance = self._distance(line=line, pivots=line.pivots)
                line.distance_extra = self._distance(
                    line=line, pivots=line.pivots_extra
                )

                seen.add(key)

                yield line

    def _suggest_lines(self, pivots: List[int], side: Side):
        current_y = self.board.get_y(self.board.df.index[-1], side=side)
        for i in range(len(pivots) - 1):
            for j in range(i + 1, len(pivots)):
                p1 = pivots[i]
                p2 = pivots[j]

                if p2 - p1 < self.board.size * self.min_pivot_distance:
                    continue

                line = ALineCandidate(
                    side=side,
                    x1=p1,
                    y1=self.board.get_y(p1, side=side),
                    x2=p2,
                    y2=self.board.get_y(p2, side=side),
                )

                line_y = line.get_y(self.board.size - 1)
                if side == Side.LOW:
                    max_diff = (
                        self.board.size / 2
                        if current_y > line_y
                        else self.board.size / 10
                    )
                else:
                    max_diff = (
                        self.board.size / 2
                        if current_y < line_y
                        else self.board.size / 5
                    )
                if abs(line_y - current_y) > max_diff:
                    continue

                yield line

    def _cluster(self, lines: List[ALineCandidate]):
        to_remove = set()
        sizes = []
        for line in lines:
            sizes.append(len(line.pivots))
        median_size = median(sizes)

        for i in range(len(lines) - 1):
            for j in range(i + 1, len(lines)):
                if len(lines[i].pivots & lines[j].pivots) >= 2:
                    si = len(lines[i].pivots) / median_size
                    sj = len(lines[j].pivots) / median_size
                    qi = lines[i].distance + lines[i].distance_extra / 4
                    qj = lines[j].distance + lines[j].distance_extra / 4
                    if si * qi > sj * qj:
                        to_remove.add(i)
                    else:
                        to_remove.add(j)

        return [line for n, line in enumerate(lines) if n not in to_remove]

    def _distance(self, line: ALineCandidate, pivots: List[int]):
        """How far the dots from the line."""
        distances = []
        for pivot in pivots:
            distances.append(
                line.get_distance(pivot, self.board.get_y(pivot, side=line.side))
            )
        if len(distances) == 1:
            return distances[0]
        return math.sqrt(sum([d * d for d in distances]))

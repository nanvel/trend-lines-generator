import math
from typing import List

import numpy as np

from .models import Board, Line, LineCandidate, Side, Time
from .utils import find_significant


class Generator:
    def __init__(self, board: Board):
        self.board = board

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
        return list(self._call())

    def _call(self):
        for side in [Side.LOW, Side.HIGH]:
            hlines = list(
                self._filter_lines(
                    lines=self._suggest_hlines(
                        pivots=[p for p, _ in self.pivots[side]],
                        side=side,
                    ),
                    side=side,
                    min_pivots=2,
                )
            )

            alines = list(
                self._filter_lines(
                    lines=self._suggest_alines(
                        pivots=[p for p, _ in self.pivots[side]],
                        side=side,
                    ),
                    side=side,
                    min_pivots=3,
                )
            )

            to_remove = set()
            for i in range(len(hlines) - 1):
                pivots_i = {a for a, _ in hlines[i].pivots}
                for j in range(i + 1, len(hlines)):
                    pivots_j = {a for a, _ in hlines[j].pivots}
                    if pivots_i & pivots_j:
                        if hlines[i].quality > hlines[j].quality:
                            to_remove.add(j)
                        else:
                            to_remove.add(i)

            hlines = [line for n, line in enumerate(hlines) if n not in to_remove]

            to_remove = set()
            for i in range(len(alines) - 1):
                pivots_i = {a for a, _ in alines[i].pivots}
                for hline in hlines:
                    pivots_j = {a for a, _ in hline.pivots}
                    if len(pivots_i & pivots_j) > 1:
                        to_remove.add(i)

            alines = [line for n, line in enumerate(alines) if n not in to_remove]

            to_remove = set()
            for i in range(len(alines) - 1):
                pivots_i = {a for a, _ in alines[i].pivots}
                for j in range(i + 1, len(alines)):
                    pivots_j = {a for a, _ in alines[j].pivots}
                    if len(pivots_i & pivots_j) > 1:
                        if alines[i].quality > alines[j].quality:
                            to_remove.add(j)
                        else:
                            to_remove.add(i)

            alines = [line for n, line in enumerate(alines) if n not in to_remove]

            for line in alines + hlines:
                yield self._to_line(line)

    def _to_line(self, line: LineCandidate):
        x1, y1 = self.board.translate(line.x1, line.y1)
        x2, y2 = self.board.translate(line.x2, line.y2)

        if self.board.x_is_datetime:
            x1 = Time.from_datetime(x1)
            x2 = Time.from_datetime(x2)

        a = (y2 - y1) / (x2 - x1)
        b = y2 - a * x2

        x_start = (
            list(sorted(line.pivots + line.pivots_opposite, key=lambda p: p[0]))[0][0]
            * self.board.x_step
            + self.board.x_start
        )

        distances = [i[1] ** 2 for i in line.pivots + line.pivots_opposite]
        width = math.sqrt(sum(distances) / len(distances))

        return Line(
            side=line.side,
            a=a,
            b=b,
            width=width * self.board.y_step,
            x_start=x_start,
        )

    def _filter_lines(self, lines, side: Side, min_pivots):
        seen = set()
        for line in lines:
            key = (line.a, line.b)
            if key in seen:
                continue

            for x, y in self.pivots[side]:
                distance = abs(line.get_distance(x, y))
                if distance <= self.band:
                    line.pivots.append((x, distance))

            if len(line.pivots) < min_pivots:
                continue

            for x, y in self.pivots[side.opposite(side)]:
                distance = abs(line.get_distance(x, y))
                if distance <= self.band:
                    line.pivots_opposite.append((x, distance))

            line.quality = self._quality(line=line)

            seen.add(key)

            yield line

    def _suggest_alines(self, pivots: List[int], side: Side):
        current_y = self.board.get_y(self.board.df.index[-1], side=side)
        for i in range(len(pivots) - 1):
            for j in range(i + 1, len(pivots)):
                p1 = pivots[i]
                p2 = pivots[j]

                if p2 - p1 < self.board.size / 10:
                    continue

                line = LineCandidate(
                    side=side,
                    x1=p1,
                    y1=self.board.get_y(p1, side=side),
                    x2=p2,
                    y2=self.board.get_y(p2, side=side),
                )

                line_y = line.get_y(self.board.size - 1)
                if abs(line_y - current_y) > self.board.size:
                    continue

                yield line

    def _suggest_hlines(self, pivots: List[int], side: Side):
        significant = find_significant(
            start=self.board.y_start,
            stop=self.board.y_start + self.board.y_step * self.board.size,
        )
        significant = [
            (s - self.board.y_start) / self.board.y_step for s in significant
        ]

        current_y = self.board.get_y(self.board.df.index[-1], side=side)
        for pivot in pivots:
            y = self.board.get_y(pivot, side=side)

            if abs(y - current_y) > self.board.size:
                continue

            for s in significant:
                if abs(s - y) <= self.band:
                    continue

            yield LineCandidate(
                side=side,
                x1=pivot,
                y1=y,
                x2=self.board.size,
                y2=y,
            )

        for s in significant:
            line = LineCandidate(
                side=side,
                x1=0,
                y1=s,
                x2=self.board.size,
                y2=s,
            )
            line.pivots.append((0, 0))
            yield line

    def _quality(self, line: LineCandidate):
        distances = []
        for pivot, distance in line.pivots:
            distances.append(distance)
        for pivot, distance in line.pivots_opposite:
            distances.append(distance + self.band)

        skip_first = 1 if line.is_horizontal else 2
        distances = list(sorted(distances))[skip_first:]
        q = 0.0
        min_distance = self.band / 10.0
        for n, distance in enumerate(distances):
            if distance < min_distance:
                distance = min_distance

            q += self.band / distance / (2**n)

        return q

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
            lines = self._cluster_lines(
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
                distance = abs(line.get_distance(x, y))
                if distance <= self.band:
                    line.pivots.append((x, distance))

            if len(line.pivots) > 2:
                for x, y in self.pivots[side.opposite(side)]:
                    distance = abs(line.get_distance(x, y))
                    if distance <= self.band:
                        line.pivots_opposite.append((x, distance))

                line.quality = self._quality(line=line)

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
                if abs(line_y - current_y) > self.board.size / 2:
                    continue

                yield line

    def _cluster_lines(self, lines: List[ALineCandidate]):
        to_remove = set()
        for i in range(len(lines) - 1):
            pivots_i = {a for a, _ in lines[i].pivots}
            for j in range(i + 1, len(lines)):
                pivots_j = {a for a, _ in lines[j].pivots}
                if len(pivots_i & pivots_j) >= 2:
                    if lines[i].quality > lines[j].quality:
                        to_remove.add(j)
                    else:
                        to_remove.add(i)

        return [line for n, line in enumerate(lines) if n not in to_remove]

    def _quality(self, line: ALineCandidate):
        distances = []
        for pivot, distance in line.pivots:
            distances.append(distance)
        for pivot, distance in line.pivots_opposite:
            distances.append(distance + self.band)

        distances = list(sorted(distances))[2:]
        q = 0.0
        min_distance = self.band / 10.0
        for n, distance in enumerate(distances):
            if distance < min_distance:
                distance = min_distance

            q += self.band / distance / (2**n)

        return q

from typing import List, Optional

from pandas import Series

from tlines.models import ALine, ALineCandidate, Board, Side, Time


class GenerateALines:
    def __init__(
        self,
        board: Board,
        max_angle: float = 60.0,
        min_angle: Optional[float] = 10.0,
        min_pivot_distance: float = 0.1,
    ):
        self.board = board
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.min_pivot_distance = min_pivot_distance

        self.max_y_distance = max(
            board.df[Side.LOW].diff().abs().median(),
            board.df[Side.HIGH].diff().abs().median(),
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

            if self.min_angle is not None:
                lines = [line for line in lines if abs(line.angle) > self.min_angle]

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
                if abs(y - line.get_y(x)) <= self.max_y_distance:
                    line.pivots.add(x)
            if len(line.pivots) >= 3:
                for x, y in self.pivots[side.opposite(side)]:
                    if abs(y - line.get_y(x)) <= self.max_y_distance:
                        line.pivots_extra.add(x)

                line.contrast = self._contrast(line=line)

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
                if abs(line.angle) > self.max_angle:
                    continue

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
        for i in range(len(lines) - 1):
            for j in range(i + 1, len(lines)):
                if len(lines[i].pivots & lines[j].pivots) >= 2:
                    if len(lines[i].pivots) > len(lines[j].pivots):
                        to_remove.add(j)
                    elif len(lines[i].pivots) < len(lines[j].pivots):
                        to_remove.add(i)
                    elif len(lines[i].pivots_extra) > len(lines[j].pivots_extra):
                        to_remove.add(j)
                    elif len(lines[i].pivots_extra) < len(lines[j].pivots_extra):
                        to_remove.add(i)
                    elif lines[i].contrast < lines[j].contrast:
                        to_remove.add(j)
                    elif lines[i].contrast > lines[j].contrast:
                        to_remove.add(i)

        return [line for n, line in enumerate(lines) if n not in to_remove]

    def _contrast(self, line: ALineCandidate):
        line_prices = Series([line.get_y(i) for i in self.board.df.index])
        if line.side == Side.LOW:
            s = self.board.df["low"] - line_prices
        else:
            s = line_prices - self.board.df["high"]
        return s[s < 0].abs().sum() / s[s >= 0].sum()

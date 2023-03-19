from dataclasses import dataclass

from .side import Side


@dataclass(frozen=True)
class HLine:
    side: Side
    y: float

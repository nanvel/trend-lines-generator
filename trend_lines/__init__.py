from typing import List, Optional

from pandas import Series

from .factories import BoardFactory
from .generator import Generator
from .models import Side, Line


__all__ = ("generate_trend_lines", "Line", "Side")


def generate_trend_lines(
    low_series: Series, high_series: Optional[Series] = None
) -> List[Line]:
    board = BoardFactory().from_series(low_series=low_series, high_series=high_series)

    return Generator(board=board)()

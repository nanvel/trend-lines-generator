import pytest
from pandas import DataFrame

from trend_lines.generator import Generator
from trend_lines.models import Board, Side


@pytest.fixture
def board():
    points = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 4, 5, 6]
    df = DataFrame({Side.LOW: points, Side.HIGH: points})
    df[Side.HIGH] += 1

    return Board(df=df, x_is_datetime=False, x_start=0, x_step=1, y_start=0, y_step=1)


def test_generate_lines(board):
    lines = Generator(board=board)()

    assert len(lines) == 1
    line = lines[0]

    assert line.side == Side.LOW
    assert line.a == 0
    assert line.b == 1
    assert round(line.width * 10) == 7
    assert line.x_start == 0
    assert line.is_horizontal

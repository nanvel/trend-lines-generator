import pytest
from pandas import DataFrame

from tlines.models import Board, Side
from tlines.use_cases import GenerateALines


@pytest.fixture
def board():
    points = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 4, 5, 6]
    df = DataFrame({Side.LOW: points, Side.HIGH: points})
    df[Side.HIGH] += 1

    return Board(df=df, x_is_datetime=False, x_start=0, x_step=1, y_start=0, y_step=1)


def test_generate_alines(board):
    lines = GenerateALines(board=board)()
    print(list(lines))

    assert False

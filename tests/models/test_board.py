import pytest
from pandas import DataFrame

from tlines.models import Board, Side


@pytest.fixture
def board():
    points = [8, 4, 6, 10, 18, 12, 8, 11, 16, 4, 0, 6, 12, 17, 11, 10, 9, 8, 9, 8]
    df = DataFrame({Side.LOW: points, Side.HIGH: points})
    df[Side.HIGH] += 1

    return Board(df=df, x_is_datetime=False, x_start=0, x_step=1, y_start=0, y_step=1)


def test_board(board):
    assert board.size == 20
    assert board.get_y(x=0, side=Side.LOW) == 8
    assert board.get_pivots(side=Side.LOW) == [1, 10]
    assert board.get_pivots(side=Side.HIGH) == [4, 8, 13]

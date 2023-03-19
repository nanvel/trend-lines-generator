from tlines.factories import BoardFactory
from tlines.models import Side


def test_from_series(data):
    df = data.load_df(path="example.csv")

    board = BoardFactory().from_series(low_series=df["low"], high_series=df["high"])

    assert board.x_is_datetime
    assert set(board.df.columns) == {Side.HIGH, Side.LOW}
    assert len(board.df) == 6
    assert board.x_start == 1677971100
    assert board.x_step == 60

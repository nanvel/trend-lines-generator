from pandas import DataFrame

from tlines.factories import BoardFactory
from tlines.models import Side


def test_from_series():
    df = (
        DataFrame(
            {
                "ts": [
                    "2023-03-04 23:05:00",
                    "2023-03-04 23:07:00",
                    "2023-03-04 23:08:00",
                    "2023-03-04 23:09:00",
                    "2023-03-04 23:10:00",
                ],
                "high": [0.07405, 0.07404, 0.07408, 0.07408, 0.07414],
                "low": [0.07401, 0.07403, 0.07394, 0.07399, 0.07408],
            }
        )
        .astype({"ts": "datetime64[s]"})
        .set_index("ts")
    )

    board = BoardFactory().from_series(low_series=df["low"], high_series=df["high"])

    assert board.x_is_datetime
    assert set(board.df.columns) == {Side.HIGH, Side.LOW}
    assert len(board.df) == 6
    assert board.x_start == 1677971100
    assert board.x_step == 60

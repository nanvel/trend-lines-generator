import requests
import mplfinance as mpf
from numpy import NaN
from pandas import DataFrame, to_datetime

from tlines.factories import BoardFactory
from tlines.models import Side
from tlines.use_cases.generate_alines import GenerateALines


def main():
    columns = [
        ("ts", "int"),
        ("volume_quote", "float64"),
        ("open", "float64"),
        ("high", "float64"),
        ("low", "float64"),
        ("close", "float64"),
    ]
    url = "https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair=DOGE_USDT&interval=1d&limit=100"
    response = requests.get(url)

    rows = response.json()

    df = (
        DataFrame([r[: len(columns)] for r in rows], columns=[i[0] for i in columns])
        .astype(dict(columns))
        .set_index("ts")
    )
    df.index = to_datetime(df.index, unit="s")

    board = BoardFactory().from_series(low_series=df["low"], high_series=df["high"])
    alines = list(GenerateALines(board=board)())

    for side in (Side.LOW, Side.HIGH):
        pivots = board.get_pivots(side=side)
        key = f"{side}_pivots"
        df[key] = NaN
        for x, y in (board.translate(p, board.get_y(p, side=side)) for p in pivots):
            df.loc[x, key] = y

    ap = [
        mpf.make_addplot(
            df["low_pivots"],
            panel=0,
            color="green",
            type="scatter",
            marker="o",
        ),
        mpf.make_addplot(
            df["high_pivots"],
            panel=0,
            color="red",
            type="scatter",
            marker="o",
        ),
    ]

    x1 = df.index[0]
    x2 = df.index[-1]

    mpf.plot(
        df,
        type="candle",
        addplot=ap,
        tight_layout=True,
        alines=[((x1, line.get_y(x1)), (x2, line.get_y(x2))) for line in alines],
    )


if __name__ == "__main__":
    main()

import requests
import mplfinance as mpf
from pandas import DataFrame, to_datetime

from trend_lines import generate_trend_lines, Side


def main():
    columns = [
        ("ts", "int"),
        ("volume_quote", "float64"),
        ("open", "float64"),
        ("high", "float64"),
        ("low", "float64"),
        ("close", "float64"),
    ]
    url = "https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair=BTC_USDT&interval=1d&limit=100"
    response = requests.get(url)

    rows = response.json()

    df = (
        DataFrame([r[: len(columns)] for r in rows], columns=[i[0] for i in columns])
        .astype(dict(columns))
        .set_index("ts")
    )
    df.index = to_datetime(df.index, unit="s")

    lines = generate_trend_lines(low_series=df["low"], high_series=df["high"])

    x1 = df.index[0]
    x2 = df.index[-1]

    mpf.plot(
        df,
        type="candle",
        tight_layout=True,
        alines={
            "alines": [((x1, line.get_y(x1)), (x2, line.get_y(x2))) for line in lines],
            "colors": ["g" if line.side == Side.LOW else "r" for line in lines],
        },
    )


if __name__ == "__main__":
    main()

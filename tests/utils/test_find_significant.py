import pytest

from trend_lines.utils import find_significant


@pytest.mark.parametrize(
    "start,stop,result",
    [
        (10, 100, [10.0, 100.0]),
        (10, 126, [10.0, 100.0]),
        (0.065, 0.1, [0.1]),
        (0.02, 0.095, [0.05]),
        (1, 1.55, [1.0]),
        (1.05, 1.55, []),
        (1.05, 2.55, [2.0, 2.5]),
        (18000, 28000, [20000, 25000]),
        (1, 100, [1, 10, 100]),
    ],
)
def test_find_significant(start, stop, result):
    assert find_significant(start=start, stop=stop) == result

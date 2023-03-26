from tlines.utils import find_significant


def test_find_significant():
    result = find_significant(start=10, stop=100)
    assert result == [10.0, 100.0]

    result = find_significant(start=10, stop=126)
    assert result == [10.0, 100.0]

    result = find_significant(start=0.065, stop=0.1)
    assert result == [0.1]

    result = find_significant(start=0.02, stop=0.095)
    assert result == [0.05]

    result = find_significant(start=1, stop=1.55)
    assert result == [1.0]

    result = find_significant(start=1.05, stop=1.55)
    assert result == []

    result = find_significant(start=1.05, stop=2.55)
    assert result == [2.0, 2.5]

    result = find_significant(start=18000, stop=28000)
    assert result == [20000, 25000]

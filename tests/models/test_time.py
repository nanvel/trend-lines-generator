import datetime

from tlines.models import Time


def test_time():
    time = Time(1679218543)

    assert str(time) == "2023-03-19 09:35"
    assert repr(time) == "Time(1679218543)"
    assert time.to_datetime() == datetime.datetime(2023, 3, 19, 9, 35, 43)


def test_from_datetime():
    time = Time.from_datetime(datetime.datetime(2023, 3, 19, 9, 35, 43))

    assert time == 1679218543

from tlines.models import ALine, ALineCandidate, Side


def test_aline_candidate():
    line = ALineCandidate(
        side=Side.LOW,
        x1=1,
        y1=1,
        x2=9,
        y2=3,
    )

    assert line.a == 0.25
    assert line.b == 0.75
    assert int(line.angle) == 14
    assert str(line) == "ALine[1,1.00 9,3.00 a14]"
    assert line.get_y(10) == 3.25


def test_aline():
    line = ALine(side=Side.LOW, a=1, b=1)

    assert line.get_y(10) == 11

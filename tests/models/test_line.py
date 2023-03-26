from trend_lines.models import Line, LineCandidate, Side


def test_line_candidate():
    line = LineCandidate(
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
    assert round(line.get_distance(1, 2) * 100) == -97
    assert round(line.get_distance(7, 1) * 100) == 146


def test_aline():
    line = Line(side=Side.LOW, a=1, b=1, width=0.1, x_start=1)

    assert line.get_y(10) == 11

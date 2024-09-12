import pytest

from musiclib.interval import AbstractInterval


@pytest.mark.parametrize(
    ('interval'), [0, 1, 12, 13, -1, -12, -13],
)
def test_init(interval):
    assert AbstractInterval(interval).interval == interval % 12


@pytest.mark.parametrize(
    ('string', 'expected'), [
        ('0', AbstractInterval(0)),
        ('A', AbstractInterval(10)),
        ('B', AbstractInterval(11)),
        ('10', AbstractInterval(0)),
        ('11', AbstractInterval(1)),
        ('1A', AbstractInterval(10)),
        ('A3', AbstractInterval(3)),
    ],
)
def test_from_str(string, expected):
    assert AbstractInterval.from_str(string) == expected


@pytest.mark.parametrize(
    ('x', 's', 'r'), [
        (AbstractInterval(3), '3', 'AbstractInterval(3)'),
        (AbstractInterval(10), 'A', 'AbstractInterval(A)'),
    ],
)
def test_str_repr(x, s, r):
    assert str(x) == s
    assert repr(x) == r


def test_sorted():
    intervals = 11, 2, 3
    assert sorted(map(AbstractInterval, intervals)) == list(map(AbstractInterval, sorted(intervals)))

import pytest

from musiclib.intervalset import IntervalSet


@pytest.mark.parametrize(
    ('bits', 'intervals'), [
        ('101011010101', frozenset({0, 2, 4, 5, 7, 9, 11})),
        ('110101101010', frozenset({0, 1, 3, 5, 6, 8, 10})),
        ('101001010100', frozenset({0, 2, 5, 7, 9})),
        ('101101010010', frozenset({0, 2, 3, 5, 7, 10})),
        ('000000000000', frozenset()),
    ],
)
def test_bits(bits, intervals):
    assert IntervalSet.from_bits(bits).intervals == intervals
    assert IntervalSet(intervals).bits == bits

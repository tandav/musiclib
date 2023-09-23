import pytest
from musiclib.util import etc


@pytest.mark.parametrize(
    ('a', 'expected'), [
        ([0, 0, 0, 0, 0], [0, 1, 2, 3, 4]),
        ([0, 0, 0, 1, 2], [0, 1, 2, 3, 4]),
        ([0, 0, 0, 3, 4], [0, 1, 2, 3, 4]),
        ([0, 0, 0, 5, 6], [0, 1, 2, 5, 6]),
        ([0, 0, 0, 1, 2, 5, 6], [0, 1, 2, 3, 4, 5, 6]),
        ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
        ([0, 0, 1, 1, 2], [0, 1, 2, 3, 4]),
        ([0, 1, 1, 2, 2], [0, 1, 2, 3, 4]),
    ],
)
def test_increment_duplicates(a, expected):
    assert etc.increment_duplicates(a) == expected

@pytest.mark.parametrize(
    ('bits', 'intervals'), [
        ('101011010101', frozenset({0, 2, 4, 5, 7, 9, 11})),
        ('110101101010', frozenset({0, 1, 3, 5, 6, 8, 10})),
        ('101001010100', frozenset({0, 2, 5, 7, 9})),
        ('101101010010', frozenset({0, 2, 3, 5, 7, 10})),
        ('000000000000', frozenset()),
    ],
)
def test_bits_intervals(bits, intervals):
    assert etc.bits_to_intervals(bits) == intervals
    assert etc.intervals_to_bits(intervals) == bits


@pytest.mark.parametrize(
    ('intervals', 'expected'), [
        (frozenset({0, 4, 7}), (frozenset({0, 4, 7}), frozenset({0, 3, 8}), frozenset({0, 5, 9}))),
        (frozenset({0, 3, 6, 9}), (
            frozenset({0, 3, 6, 9}),
            frozenset({0, 3, 6, 9}),
            frozenset({0, 3, 6, 9}),
            frozenset({0, 3, 6, 9}),
        )),
        (frozenset({0, 2, 4, 5, 7, 9, 11}), (
            frozenset({0, 2, 4, 5, 7, 9, 11}),
            frozenset({0, 2, 3, 5, 7, 9, 10}),
            frozenset({0, 1, 3, 5, 7, 8, 10}),
            frozenset({0, 2, 4, 6, 7, 9, 11}),
            frozenset({0, 2, 4, 5, 7, 9, 10}),
            frozenset({0, 2, 3, 5, 7, 8, 10}),
            frozenset({0, 1, 3, 5, 6, 8, 10}),
        )),
    ],
)
def test_intervals_rotations(intervals, expected):
    assert etc.intervals_rotations(intervals) == expected

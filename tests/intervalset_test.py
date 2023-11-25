import pytest
from musiclib.interval import AbstractInterval
from musiclib.intervalset import IntervalSet


@pytest.mark.parametrize(
    ('bits', 'intervals'), [
        ('101011010101', frozenset({0, 2, 4, 5, 7, 9, 11})),
        ('110101101010', frozenset({0, 1, 3, 5, 6, 8, 10})),
        ('101001010100', frozenset({0, 2, 5, 7, 9})),
        ('100001000100', frozenset({0, 5, 9})),
        ('101101010010', frozenset({0, 2, 3, 5, 7, 10})),
        ('000000000000', frozenset()),
    ],
)
def test_bits(bits, intervals):
    intervals = frozenset(map(AbstractInterval, intervals))
    assert IntervalSet.from_bits(bits).intervals == intervals
    assert IntervalSet(intervals).bits == bits


@pytest.mark.parametrize(
    ('name'), [
        'major',
        'dim7_1',
        'sus2_0',
    ],
)
def test_from_name(name):
    assert name in IntervalSet.from_name(name).names


@pytest.mark.parametrize(
    ('x', 's', 'r'), [
        (IntervalSet(frozenset(map(AbstractInterval, {0, 4, 7}))), '0_4_7', 'IntervalSet(0 4 7)'),
    ],
)
def test_str_repr(x, s, r):
    assert str(x) == s
    assert repr(x) == r


@pytest.mark.parametrize(
    ('intervalset', 'names'), [
        ({0, 2, 4, 5, 7, 9, 11}, frozenset({'major'})),
        ({0, 1, 3, 5, 7, 8, 10}, frozenset({'phrygian'})),
        ({0, 3, 5, 8, 10}, frozenset({'p_phrygian'})),
        ({0, 4, 7}, frozenset({'major_0'})),
        ({0, 3, 6}, frozenset({'dim_0'})),
        ({0, 3, 6, 9}, frozenset({'dim7_0', 'dim7_1', 'dim7_2', 'dim7_3'})),
        ({0, 4, 8}, frozenset({'aug_0', 'aug_1', 'aug_2'})),
        ({0, 3, 6, 10}, frozenset({'half-dim7_0', 'm6_3'})),
        ({0, 3, 7, 10}, frozenset({'6_3', 'min7_0'})),
        ({0, 4, 7, 9}, frozenset({'6_0', 'min7_1'})),
        ({0, 3, 5, 8}, frozenset({'6_1', 'min7_2'})),
        ({0, 2, 5, 9}, frozenset({'6_2', 'min7_3'})),
        ({0, 3, 7, 9}, frozenset({'half-dim7_1', 'm6_0'})),
        ({0, 4, 6, 9}, frozenset({'half-dim7_2', 'm6_1'})),
        ({0, 2, 5, 8}, frozenset({'half-dim7_3', 'm6_2'})),
        ({0, 2, 7}, frozenset({'sus2_0', 'sus4_1'})),
        ({0, 5, 10}, frozenset({'sus2_1', 'sus4_2'})),
        ({0, 5, 7}, frozenset({'sus2_2', 'sus4_0'})),
    ],
)
def test_names(intervalset, names):
    intervalset = IntervalSet(frozenset(map(AbstractInterval, intervalset)))
    assert intervalset.names == names
    for name in names:
        assert IntervalSet.from_name(name).intervals == intervalset.intervals


@pytest.mark.parametrize(
    ('intervalset', 'expected'), [
        ({0, 2, 4, 5, 7, 9, 11}, {'major': 'natural'}),
        ({0, 2, 4, 7, 9}, {'p_major': 'pentatonic'}),
        # chords
        ({0, 4, 7}, {'major_0': 'major'}),
        ({0, 3, 8}, {'major_1': 'major'}),
        ({0, 5, 9}, {'major_2': 'major'}),
        ({0, 4, 7, 10}, {'7_0': '7'}),
        ({0, 3, 6, 8}, {'7_1': '7'}),
        ({0, 3, 5, 9}, {'7_2': '7'}),
        ({0, 2, 6, 9}, {'7_3': '7'}),
        ({0, 3, 6, 9}, {'dim7_0': 'dim7', 'dim7_1': 'dim7', 'dim7_2': 'dim7', 'dim7_3': 'dim7'}),
        ({0, 4, 8}, {'aug_1': 'aug', 'aug_2': 'aug', 'aug_0': 'aug'}),
        ({0, 3, 6, 10}, {'half-dim7_0': 'half-dim7', 'm6_3': 'm6'}),
        ({0, 3, 7, 10}, {'min7_0': 'min7', '6_3': '6'}),
        ({0, 4, 7, 9}, {'min7_1': 'min7', '6_0': '6'}),
        ({0, 3, 5, 8}, {'6_1': '6', 'min7_2': 'min7'}),
        ({0, 2, 5, 9}, {'min7_3': 'min7', '6_2': '6'}),
        ({0, 3, 7, 9}, {'m6_0': 'm6', 'half-dim7_1': 'half-dim7'}),
        ({0, 4, 6, 9}, {'half-dim7_2': 'half-dim7', 'm6_1': 'm6'}),
        ({0, 2, 5, 8}, {'m6_2': 'm6', 'half-dim7_3': 'half-dim7'}),
        ({0, 3, 6, 9}, {'dim7_0': 'dim7', 'dim7_2': 'dim7', 'dim7_3': 'dim7', 'dim7_1': 'dim7'}),
        ({0, 2, 7}, {'sus2_0': 'sus2', 'sus4_1': 'sus4'}),
        ({0, 5, 10}, {'sus4_2': 'sus4', 'sus2_1': 'sus2'}),
        ({0, 5, 7}, {'sus2_2': 'sus2', 'sus4_0': 'sus4'}),
    ],
)
def test_name_kinds(intervalset, expected):
    intervalset = IntervalSet(frozenset(map(AbstractInterval, intervalset)))
    assert intervalset.name_kinds == expected


@pytest.mark.parametrize(
    ('intervalset', 'expected'), [
        ({0, 2, 4, 5, 7, 9, 11}, {0, 1, 3, 5, 7, 8, 10}),
        ({0, 2, 3, 5, 7, 9, 10}, {0, 2, 3, 5, 7, 9, 10}),
    ],
)
def test_inverse(intervalset, expected):
    intervalset = IntervalSet(frozenset(map(AbstractInterval, intervalset)))
    expected = IntervalSet(frozenset(map(AbstractInterval, expected)))
    assert intervalset.inverse == expected
    assert intervalset.inverse.inverse == intervalset

import pytest

from musiclib.noteset import SpecificNoteSet
from musiclib.voice_leading import checks


@pytest.mark.parametrize(
    ('f', 'extra_args'), [
        (checks.is_parallel_interval, (7,)),
        (checks.is_hidden_parallel, (7,)),
        (checks.is_voice_crossing, ()),
        (checks.is_large_leaps, (4,)),
    ],
)
def test_cache(f, extra_args):
    a = SpecificNoteSet.from_str('C5653_E2895_G1111')
    b = SpecificNoteSet.from_str('F5384_A5559_C6893')
    c = SpecificNoteSet.from_str('d5653_F2895_a1111')
    d = SpecificNoteSet.from_str('f5384_b5559_d6893')

    assert f._cache_info['hits'] == 0
    assert f._cache_info['misses'] == 0
    assert f._cache_info['currsize'] == 0
    f(a, b, *extra_args)
    assert f._cache_info['hits'] == 0
    assert f._cache_info['misses'] == 1
    assert f._cache_info['currsize'] == 1
    f(a, b, *extra_args)
    assert f._cache_info['hits'] == 1
    assert f._cache_info['misses'] == 1
    assert f._cache_info['currsize'] == 1
    f(c, d, *extra_args)
    assert f._cache_info['hits'] == 2
    assert f._cache_info['misses'] == 1
    assert f._cache_info['currsize'] == 1


def test_parallel_interval():
    # fifths
    a = SpecificNoteSet.from_str('C5_E5_G5')
    b = SpecificNoteSet.from_str('F5_A5_C6')
    c = SpecificNoteSet.from_str('C5_F5_A5')
    d = SpecificNoteSet.from_str('C5_E5_B5')
    h = SpecificNoteSet.from_str('D5_F5_A5')
    i = SpecificNoteSet.from_str('C5_E5_G6')
    j = SpecificNoteSet.from_str('F5_A5_C7')

    assert checks.is_parallel_interval(a, b, 7)
    assert checks.is_parallel_interval(a, h, 7)
    assert checks.is_parallel_interval(i, j, 7)
    assert not checks.is_parallel_interval(a, c, 7)
    assert not checks.is_parallel_interval(a, d, 7)

    # octaves
    e = SpecificNoteSet.from_str('C5_E5_C6')
    f = SpecificNoteSet.from_str('D5_F5_D6')
    g = SpecificNoteSet.from_str('C5_E5_E6')
    assert checks.is_parallel_interval(e, f, 0)
    assert not checks.is_parallel_interval(g, f, 0)


def test_hidden_parallel():
    a = SpecificNoteSet.from_str('E5_G5_C6')
    b = SpecificNoteSet.from_str('F5_A5_F6')
    c = SpecificNoteSet.from_str('F5_G5_C6')
    d = SpecificNoteSet.from_str('F5_A5_C6')
    e = SpecificNoteSet.from_str('C5_B5')
    f = SpecificNoteSet.from_str('D5_D7')
    g = SpecificNoteSet.from_str('C5_E5_F5')
    h = SpecificNoteSet.from_str('D5_F5_A5')
    i = SpecificNoteSet.from_str('D5_F5_A6')
    assert checks.is_hidden_parallel(a, b, 0)
    assert checks.is_hidden_parallel(e, f, 0)
    assert checks.is_hidden_parallel(g, h, 7)
    assert checks.is_hidden_parallel(g, i, 7)
    assert not checks.is_hidden_parallel(c, b, 0)
    assert not checks.is_hidden_parallel(c, d, 0)


def test_voice_crossing():
    assert checks.is_voice_crossing(SpecificNoteSet.from_str('E3_E5_G5_B5'), SpecificNoteSet.from_str('A3_C4_E4_A4'))


@pytest.mark.parametrize(
    ('a', 'b', 'interval', 'expected'), [
        ('C1_E1', 'C2_E2', 5, True),
        ('C1_E1', 'E1_G1', 5, False),
        ('C1_E1', 'F1_G1', 5, False),
        ('C1_E1', 'f1_G1', 5, True),
        ('C1', 'F1', 5, False),
        ('C1', 'f1', 5, True),
    ],
)
def test_large_leaps(a, b, interval, expected):
    assert checks.is_large_leaps(SpecificNoteSet.from_str(a), SpecificNoteSet.from_str(b), interval) == expected


@pytest.mark.parametrize(
    ('chord_str', 'max_interval', 'expected'), [
        ('C1_d2', 12, True),
        ('C1_C2', 12, False),
        ('C1_d1', 1, False),
        ('C1_D1', 1, True),
        ('B0_C1', 2, False),
        ('B0_d1', 2, False),
        ('B0_D1', 2, True),
    ],
)
def test_large_spacing(chord_str, max_interval, expected):
    assert checks.is_large_spacing(SpecificNoteSet.from_str(chord_str), max_interval) == expected


@pytest.mark.parametrize(
    ('chord_str', 'min_interval', 'expected'), [
        ('C1_d2', 12, False),
        ('C1_C2', 13, True),
        ('C1_d1', 1, False),
        ('C1_d1', 2, True),
        ('C1_D1', 1, False),
        ('C1_D1', 2, False),
        ('C1_D1', 3, True),
    ],
)
def test_small_spacing(chord_str, min_interval, expected):
    assert checks.is_small_spacing(SpecificNoteSet.from_str(chord_str), min_interval) == expected


@pytest.mark.parametrize('swap', [False, True])
@pytest.mark.parametrize(
    ('a', 'b', 'n_notes', 'expected'), [
        (SpecificNoteSet(frozenset()), SpecificNoteSet(frozenset()), 0, ()),
        (SpecificNoteSet(frozenset()), SpecificNoteSet(frozenset()), 1, ()),
        (SpecificNoteSet(frozenset()), SpecificNoteSet.from_str('C1'), 0, ()),
        (SpecificNoteSet(frozenset()), SpecificNoteSet.from_str('C1'), 1, (0,)),
        (SpecificNoteSet(frozenset()), SpecificNoteSet.from_str('C1'), 2, (0,)),
        (SpecificNoteSet.from_str('C3_E3_A3'), SpecificNoteSet.from_str('d3_B3'), 3, (1,)),
    ],
)
def test_find_paused_voices(a, b, n_notes, expected, swap):
    """TODO: test n_notes=0,1,2,3,4
    TODO: more test cases
    0 0
    0 1
    1 0
    1 1
    1 2
    2 1
    1 3
    0 3
    0 2
    0 4
    all combinations? (product(range(5), repeat=2)
    when both a and b less than n_notes
    equal distances to more (then chose 1st occurrence)
    """
    if swap:
        a, b = b, a
    assert checks.find_paused_voices(a, b, n_notes) == expected


def test_find_paused_voices_raises():
    with pytest.raises(ValueError):
        checks.find_paused_voices(SpecificNoteSet.from_str('C1_D1'), SpecificNoteSet.from_str('C1'), 1)

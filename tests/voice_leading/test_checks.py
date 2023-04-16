import pytest
from musiclib.chord import SpecificChord
from musiclib.voice_leading import checks


@pytest.mark.parametrize(
    ('f', 'extra_args'), [
        (checks.parallel_interval, (7,)),
        (checks.hidden_parallel, (7,)),
        (checks.voice_crossing, ()),
        (checks.large_leaps, (4,)),
    ],
)
def test_cache(f, extra_args):
    a = SpecificChord.from_str('C5653_E2895_G1111')
    b = SpecificChord.from_str('F5384_A5559_C6893')
    c = SpecificChord.from_str('d5653_F2895_a1111')
    d = SpecificChord.from_str('f5384_b5559_d6893')

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
    a = SpecificChord.from_str('C5_E5_G5')
    b = SpecificChord.from_str('F5_A5_C6')
    c = SpecificChord.from_str('C5_F5_A5')
    d = SpecificChord.from_str('C5_E5_B5')
    h = SpecificChord.from_str('D5_F5_A5')
    i = SpecificChord.from_str('C5_E5_G6')
    j = SpecificChord.from_str('F5_A5_C7')

    assert checks.parallel_interval(a, b, 7)
    assert checks.parallel_interval(a, h, 7)
    assert checks.parallel_interval(i, j, 7)
    assert not checks.parallel_interval(a, c, 7)
    assert not checks.parallel_interval(a, d, 7)

    # octaves
    e = SpecificChord.from_str('C5_E5_C6')
    f = SpecificChord.from_str('D5_F5_D6')
    g = SpecificChord.from_str('C5_E5_E6')
    assert checks.parallel_interval(e, f, 0)
    assert not checks.parallel_interval(g, f, 0)


def test_hidden_parallel():
    a = SpecificChord.from_str('E5_G5_C6')
    b = SpecificChord.from_str('F5_A5_F6')
    c = SpecificChord.from_str('F5_G5_C6')
    d = SpecificChord.from_str('F5_A5_C6')
    e = SpecificChord.from_str('C5_B5')
    f = SpecificChord.from_str('D5_D7')
    g = SpecificChord.from_str('C5_E5_F5')
    h = SpecificChord.from_str('D5_F5_A5')
    i = SpecificChord.from_str('D5_F5_A6')
    assert checks.hidden_parallel(a, b, 0)
    assert checks.hidden_parallel(e, f, 0)
    assert checks.hidden_parallel(g, h, 7)
    assert checks.hidden_parallel(g, i, 7)
    assert not checks.hidden_parallel(c, b, 0)
    assert not checks.hidden_parallel(c, d, 0)


def test_voice_crossing():
    assert checks.voice_crossing(SpecificChord.from_str('E3_E5_G5_B5'), SpecificChord.from_str('A3_C4_E4_A4'))


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
    assert checks.large_leaps(SpecificChord.from_str(a), SpecificChord.from_str(b), interval) == expected


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
    assert checks.large_spacing(SpecificChord.from_str(chord_str), max_interval) == expected


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
    assert checks.small_spacing(SpecificChord.from_str(chord_str), min_interval) == expected


@pytest.mark.parametrize('swap', [False, True])
@pytest.mark.parametrize(
    ('a', 'b', 'n_notes', 'expected'), [
        (SpecificChord(frozenset()), SpecificChord(frozenset()), 0, ()),
        (SpecificChord(frozenset()), SpecificChord(frozenset()), 1, ()),
        (SpecificChord(frozenset()), SpecificChord.from_str('C1'), 0, ()),
        (SpecificChord(frozenset()), SpecificChord.from_str('C1'), 1, (0,)),
        (SpecificChord(frozenset()), SpecificChord.from_str('C1'), 2, (0,)),
        (SpecificChord.from_str('C3_E3_A3'), SpecificChord.from_str('d3_B3'), 3, (1,)),
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
        checks.find_paused_voices(SpecificChord.from_str('C1_D1'), SpecificChord.from_str('C1'), 1)

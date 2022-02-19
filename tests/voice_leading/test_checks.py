import pytest

from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.voice_leading import checks


def test_have_parallel_interval():
    # fifths
    a = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}))
    b = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 6)}))
    c = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    d = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('B', 5)}))
    h = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    i = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 6)}))
    j = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 7)}))

    assert checks.have_parallel_interval(a, b, 7)
    assert checks.have_parallel_interval(a, h, 7)
    assert checks.have_parallel_interval(i, j, 7)
    assert not checks.have_parallel_interval(a, c, 7)
    assert not checks.have_parallel_interval(a, d, 7)

    # octaves
    e = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('C', 6)}))
    f = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('D', 6)}))
    g = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('E', 6)}))
    assert checks.have_parallel_interval(e, f, 0)
    assert not checks.have_parallel_interval(g, f, 0)


def test_have_hidden_parallel():
    a = SpecificChord(frozenset({SpecificNote('E', 5), SpecificNote('G', 5), SpecificNote('C', 6)}))
    b = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('F', 6)}))
    c = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('G', 5), SpecificNote('C', 6)}))
    d = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 6)}))
    e = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('B', 5)}))
    f = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('D', 7)}))
    g = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('F', 5)}))
    h = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    i = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 6)}))
    assert checks.have_hidden_parallel(a, b, 0)
    assert checks.have_hidden_parallel(e, f, 0)
    assert checks.have_hidden_parallel(g, h, 7)
    assert checks.have_hidden_parallel(g, i, 7)
    assert not checks.have_hidden_parallel(c, b, 0)
    assert not checks.have_hidden_parallel(c, d, 0)


def test_have_voice_crossing():
    assert checks.have_voice_crossing(SpecificChord.from_str('E3_E5_G5_B5'), SpecificChord.from_str('A3_C4_E4_A4'))


@pytest.mark.parametrize('a, b, interval, expected', (
    ('C1_E1', 'C2_E2', 5, True),
    ('C1_E1', 'E1_G1', 5, False),
    ('C1_E1', 'F1_G1', 5, False),
    ('C1_E1', 'f1_G1', 5, True),
    ('C1', 'F1', 5, False),
    ('C1', 'f1', 5, True),
))
def test_have_large_leaps(a, b, interval, expected):
    assert checks.have_large_leaps(SpecificChord.from_str(a), SpecificChord.from_str(b), interval) == expected


@pytest.mark.parametrize('chord_str, max_interval, expected', (
    ('C1_d2', 12, True),
    ('C1_C2', 12, False),
    ('C1_d1', 1, False),
    ('C1_D1', 1, True),
    ('B0_C1', 2, False),
    ('B0_d1', 2, False),
    ('B0_D1', 2, True),
))
def test_large_spacing(chord_str, max_interval, expected):
    assert checks.large_spacing(SpecificChord.from_str(chord_str), max_interval) == expected


@pytest.mark.parametrize('chord_str, min_interval, expected', (
    ('C1_d2', 12, False),
    ('C1_C2', 13, True),
    ('C1_d1', 1, False),
    ('C1_d1', 2, True),
    ('C1_D1', 1, False),
    ('C1_D1', 2, False),
    ('C1_D1', 3, True),
))
def test_small_spacing(chord_str, min_interval, expected):
    assert checks.small_spacing(SpecificChord.from_str(chord_str), min_interval) == expected

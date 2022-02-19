import pytest

from musictool.chord import SpecificChord
from musictool.voice_leading import checks


def test_have_parallel_interval():
    # fifths
    a = SpecificChord.from_str('C5_E5_G5')
    b = SpecificChord.from_str('F5_A5_C6')
    c = SpecificChord.from_str('C5_F5_A5')
    d = SpecificChord.from_str('C5_E5_B5')
    h = SpecificChord.from_str('D5_F5_A5')
    i = SpecificChord.from_str('C5_E5_G6')
    j = SpecificChord.from_str('F5_A5_C7')

    assert checks.have_parallel_interval(a, b, 7)
    assert checks.have_parallel_interval(a, h, 7)
    assert checks.have_parallel_interval(i, j, 7)
    assert not checks.have_parallel_interval(a, c, 7)
    assert not checks.have_parallel_interval(a, d, 7)

    # octaves
    e = SpecificChord.from_str('C5_E5_C6')
    f = SpecificChord.from_str('D5_F5_D6')
    g = SpecificChord.from_str('C5_E5_E6')
    assert checks.have_parallel_interval(e, f, 0)
    assert not checks.have_parallel_interval(g, f, 0)


def test_have_hidden_parallel():
    a = SpecificChord.from_str('E5_G5_C6')
    b = SpecificChord.from_str('F5_A5_F6')
    c = SpecificChord.from_str('F5_G5_C6')
    d = SpecificChord.from_str('F5_A5_C6')
    e = SpecificChord.from_str('C5_B5')
    f = SpecificChord.from_str('D5_D7')
    g = SpecificChord.from_str('C5_E5_F5')
    h = SpecificChord.from_str('D5_F5_A5')
    i = SpecificChord.from_str('D5_F5_A6')
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

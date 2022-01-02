import pytest

from musictools.chord import Chord
from musictools.chord import SpecificChord
from musictools.note import Note
from musictools.note import SpecificNote


def test_creation_from_notes():
    assert str(Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('C'))) == 'CEG/C'


def test_creation_from_str():
    assert str(Chord(frozenset({'C', 'E', 'G'}), root=Note('C'))) == 'CEG/C'


def test_notes():
    assert Chord(frozenset({'C', 'E', 'G'}), root=Note('C')).notes == frozenset({Note('C'), Note('E'), Note('G')})
    assert Chord.from_name('C', 'major').notes == frozenset({Note('C'), Note('E'), Note('G')})


@pytest.mark.xfail(reason='todo: sort chromatically even for abstract notes when chord is in 2 octaves')
def test_str_sort_2_octaves():
    assert str(Chord(frozenset({'B', 'D', 'F'}), root='B')) == 'BDF/B'


def test_name():
    assert Chord(frozenset({'C', 'E', 'G'}), root=Note('C')).name == 'major'
    assert Chord(frozenset({'B', 'D', 'F'}), root=Note('B')).name == 'diminished'


def test_intervals():
    assert Chord(frozenset({'C', 'E', 'G'}), root=Note('C')).intervals == frozenset({4, 7})


def test_from_name():
    assert str(Chord.from_name('C', 'major')) == 'CEG/C'


def test_from_str():
    for _ in range(10):
        chord = SpecificChord.random()
        assert SpecificChord.from_str(str(chord)) == chord


def test_root_validation():
    with pytest.raises(ValueError):
        SpecificChord(frozenset({SpecificNote('A'), SpecificNote('B')}), root=Note('E'))


def test_combinations_order():
    for _ in range(10):
        for n, m in SpecificChord.random().notes_combinations():
            assert n < m


def test_find_intervals():
    a = SpecificNote('C', 5)
    b = SpecificNote('E', 5)
    c = SpecificNote('G', 5)
    d = SpecificNote('C', 6)
    e = SpecificNote('D', 6)

    assert SpecificChord(frozenset({a, b, c})).find_intervals(7) == ((a, c),)
    assert SpecificChord(frozenset({a, b, c, e})).find_intervals(7) == ((a, c), (c, e))
    assert SpecificChord(frozenset({a, d})).find_intervals(12) == ((a, d),)

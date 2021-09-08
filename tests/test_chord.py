import pytest

from piano_scales.chord import Chord
from piano_scales.note import Note


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

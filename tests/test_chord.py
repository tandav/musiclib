from piano_scales.chord import Chord
from piano_scales.note import Note


def test_creation_from_notes():
    assert str(Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('C'))) == 'CEG/C'


def test_creation_from_str():
    assert str(Chord(frozenset({'C', 'E', 'G'}), root=Note('C'))) == 'CEG/C'


def test_name():
    assert Chord(frozenset({'C', 'E', 'G'}), root=Note('C')).name == 'major'
    assert Chord(frozenset({'B', 'D', 'F'}), root=Note('B')).name == 'diminished'


def test_intervals():
    assert Chord(frozenset({'C', 'E', 'G'}), root=Note('C')).intervals == frozenset({4, 7})


def test_from_name():
    assert str(Chord.from_name('C', 'major')) == 'CEG/C'

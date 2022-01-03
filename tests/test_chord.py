import pytest

from musictools.chord import Chord
from musictools.chord import SpecificChord
from musictools.note import Note
from musictools.note import SpecificNote


def test_creation_from_notes():
    assert str(Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('C'))) == 'CEG/C'


def test_creation_from_str():
    assert str(Chord(frozenset('CEG'), root=Note('C'))) == 'CEG/C'


def test_notes():
    assert Chord(frozenset('CEG'), root=Note('C')).notes == frozenset({Note('C'), Note('E'), Note('G')})
    assert Chord.from_name('C', 'major').notes == frozenset({Note('C'), Note('E'), Note('G')})


def test_str_sort_2_octaves():
    assert str(Chord(frozenset('BDF'), root='B')) == 'BDF/B'
    assert str(Chord(frozenset('DGBFCEA'), root='B')) == 'BCDEFGA/B'


def test_name():
    assert Chord(frozenset('CEG'), root=Note('C')).name == 'major'
    assert Chord(frozenset('BDF'), root=Note('B')).name == 'diminished'


def test_intervals():
    assert Chord(frozenset('CEG'), root=Note('C')).intervals == frozenset({4, 7})


def test_from_intervals():
    assert Chord.from_intervals('C', frozenset({4, 7})) == Chord(frozenset('CEG'), root='C')
    assert Chord.from_intervals('E', frozenset({1, 3, 5, 7, 8, 10})) == Chord(frozenset('CDEFGAB'), root='E')
    assert Chord.from_intervals('f', frozenset({2, 3, 5, 7, 9, 10})) == Chord(frozenset('faABdeE'), root='f')


def test_from_name():
    assert str(Chord.from_name('C', 'major')) == 'CEG/C'
    assert str(Chord.from_name('d', '7')) == 'dFaB/d'


def test_from_str():
    assert SpecificChord.from_str('C1_E1_G1/C') == SpecificChord(frozenset({SpecificNote('C', 1), SpecificNote('E', 1), SpecificNote('G', 1)}), root=Note('C'))
    assert Chord.from_str('CEG/C') == Chord(frozenset('CEG'), root='C')
    for _ in range(10):
        chord = SpecificChord.random()
        assert SpecificChord.from_str(str(chord)) == chord
        chord = Chord.random()
        assert Chord.from_str(str(chord)) == chord


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


@pytest.mark.parametrize(
    ('chord', 'note', 'steps', 'result'), (
    (Chord.from_str('CEG'), Note('C'), 1, Note('E')),
    (Chord.from_str('CEG'), Note('C'), 2, Note('G')),
    (Chord.from_str('CEG'), Note('C'), 3, Note('C')),
    (Chord.from_str('CeGb'), Note('e'), 2, Note('b')),
    (Chord.from_str('CeGb'), Note('e'), 25, Note('G')),
    (Chord.from_str('CEG'), Note('C'), -1, Note('G')),
    (Chord.from_str('CEG'), Note('C'), -2, Note('E')),
    (Chord.from_str('CEG'), Note('C'), -3, Note('C')),
    (Chord.from_str('CEG'), Note('C'), -3, Note('C')),
    (Chord.from_str('CeGb'), Note('e'), -15, Note('G')),
))
def test_add_note(chord, note, steps, result):
    assert chord.add_note(note, steps) == result

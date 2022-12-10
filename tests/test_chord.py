import random

import pytest

from musiclib.chord import Chord
from musiclib.chord import SpecificChord
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noteset import NoteSet


def test_creation_from_notes():
    assert str(Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('C'))) == 'CEG/C'


def test_chord_root_validation():
    with pytest.raises(TypeError):
        Chord.from_str('CEG')


@pytest.mark.parametrize('arg', ('C1_D1_E1', set('C1_D1_E1'), tuple('C1_D1_E1'), list('C1_D1_E1')))
def test_specificchord_notes_type_is_frozenset(arg):
    with pytest.raises(TypeError):
        SpecificChord(arg)


def test_specificchord_root_validation():
    assert isinstance(SpecificChord(frozenset({SpecificNote('A', 1)}), root='A').root, Note)
    with pytest.raises(KeyError):
        SpecificChord(frozenset({SpecificNote('A', 1)}), root='E')


def test_notes():
    assert Chord(frozenset(map(Note, 'CEG')), root=Note('C')).notes == frozenset({Note('C'), Note('E'), Note('G')})
    assert Chord.from_name('C', 'major').notes == frozenset({Note('C'), Note('E'), Note('G')})


@pytest.mark.parametrize(
    'chord, expected', (
        (Chord(frozenset(map(Note, 'BDF')), root=Note('B')), 'BDF/B'),
        (Chord(frozenset(map(Note, 'DGBFCEA')), root=Note('B')), 'BCDEFGA/B'),
    ),
)
def test_str_sort_2_octaves(chord, expected):
    assert str(chord) == expected


@pytest.mark.parametrize(
    'notes, root, expected', (
        ('CEG', 'C', 'major'),
        ('BDF', 'B', 'diminished'),
        ('CefA', 'C', 'dim7'),
        ('DFaC', 'D', 'half-dim7'),
    ),
)
def test_name(notes, root, expected):
    assert Chord(frozenset(map(Note, notes)), root=Note(root)).name == expected


def test_intervals():
    assert Chord.from_str('CEG/C').intervals == frozenset({0, 4, 7})


def test_from_name():
    assert str(Chord.from_name('C', 'major')) == 'CEG/C'
    assert str(Chord.from_name('d', '7')) == 'dFaB/d'


def test_from_str():
    assert SpecificChord.from_str('C1_E1_G1/C') == SpecificChord(frozenset({SpecificNote('C', 1), SpecificNote('E', 1), SpecificNote('G', 1)}), root=Note('C'))
    assert Chord.from_str('CEG/C') == Chord(frozenset(map(Note, 'CEG')), root=Note('C'))
    for _ in range(10):
        s_chord = SpecificChord.random()
        assert SpecificChord.from_str(str(s_chord)) == s_chord
        abstract_notes = SpecificNote.to_abstract(s_chord.notes)
        chord = Chord(notes=abstract_notes, root=random.choice(tuple(abstract_notes)))
        assert Chord.from_str(str(chord)) == chord
    with pytest.raises(NotImplementedError):
        SpecificChord.from_str('C1_C1')
    with pytest.raises(NotImplementedError):
        SpecificChord.from_str('C1_E1_E1')


def test_magic_methods():
    chord = SpecificChord.from_str('C1_E1_G1')
    assert len(chord) == len(chord.notes)
    assert all(chord[i] == chord.notes_ascending[i] for i in range(len(chord)))
    assert tuple(iter(chord)) == chord.notes_ascending
    chord2 = SpecificChord.from_str('d3_f8')
    assert tuple(zip(chord, chord2)) == (
        (SpecificNote('C', 1), SpecificNote('d', 3)),
        (SpecificNote('E', 1), SpecificNote('f', 8)),
    )


def test_sub():
    a = SpecificChord.from_str('C1_E1_G1')
    b = SpecificChord.from_str('B0_D1_G1')
    assert a - b == b - a == 3


def test_combinations_order():
    for _ in range(10):
        for n, m in SpecificChord.random().notes_combinations():
            assert n < m


@pytest.mark.parametrize(
    'specific, abstract', (
        ('C1_E1_G2/C', Chord.from_str('CEG/C')),
        ('C1_E1_G2', NoteSet.from_str('CEG')),
    ),
)
def test_abstract(specific, abstract):
    assert SpecificChord.from_str(specific).abstract == abstract


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
    'chord, note, steps, result', (
        (Chord.from_str('CEG/C'), Note('C'), 1, Note('E')),
        (Chord.from_str('CEG/C'), Note('C'), 2, Note('G')),
        (Chord.from_str('CEG/C'), Note('C'), 3, Note('C')),
        (Chord.from_str('CeGb/C'), Note('e'), 2, Note('b')),
        (Chord.from_str('CeGb/C'), Note('e'), 25, Note('G')),
        (Chord.from_str('CEG/C'), Note('C'), -1, Note('G')),
        (Chord.from_str('CEG/C'), Note('C'), -2, Note('E')),
        (Chord.from_str('CEG/C'), Note('C'), -3, Note('C')),
        (Chord.from_str('CEG/C'), Note('C'), -3, Note('C')),
        (Chord.from_str('CeGb/C'), Note('e'), -15, Note('G')),
    ),
)
def test_add_note(chord, note, steps, result):
    assert chord.add_note(note, steps) == result


@pytest.mark.parametrize(
    'chord, expected', (
        ('C3_E3_G3', 'C0_E0_G0'),
        ('F3_A3_C4', 'C0_E0_G0'),
        ('C3_E3_G3/C', 'C0_E0_G0/C'),
        ('F3_A3_C4/F', 'C0_E0_G0/C'),
    ),
)
def test_transposed_to_C0(chord, expected):
    assert SpecificChord.from_str(chord).transposed_to_C0 == SpecificChord.from_str(expected)


@pytest.mark.parametrize(
    'chord, add, expected', (
        ('C3_E3_G3', -36, 'C0_E0_G0'),
        ('C3_E3_G3', -24, 'C1_E1_G1'),
        ('C3_E3_G3', 0, 'C3_E3_G3'),
        ('C3_E3_G3', 12, 'C4_E4_G4'),
        ('C3_E3_G3', -34, 'D0_f0_A0'),
        ('C3_E3_G3', 13, 'd4_F4_a4'),
        ('C3_E3_G3/C', -36, 'C0_E0_G0/C'),
        ('C3_E3_G3/C', -24, 'C1_E1_G1/C'),
        ('C3_E3_G3/C', 13, 'd4_F4_a4/d'),
        ('C3_E3_G3/E', 13, 'd4_F4_a4/F'),
    ),
)
def test_add(chord, add, expected):
    assert SpecificChord.from_str(chord) + add == SpecificChord.from_str(expected)
    with pytest.raises(TypeError):
        chord + [1]

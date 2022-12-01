import operator

import pytest

from musiclib.chord import Chord
from musiclib.chord import SpecificChord
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noteset import NoteSet
from musiclib.progression import Progression
from musiclib.scale import Scale
from musiclib.util.cache import Cached


@pytest.mark.parametrize(
    'op, a, b', (
        (operator.is_, Note('A'), Note('A')),
        (operator.is_not, Note('A'), Note('B')),
    ),
)
def test_note(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    'op, a, b', (
        (operator.is_, SpecificNote('C', 1), SpecificNote('C', 1)),
        (operator.is_not, SpecificNote('C', 1), SpecificNote('C', 2)),
        (operator.is_, SpecificNote('C', 1), SpecificNote(Note('C'), 1)),
    ),
)
def test_specific_note(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    'op, a, b', (
        (operator.is_, NoteSet(frozenset(map(Note, 'CDe'))), NoteSet(frozenset(map(Note, 'CDe')))),
        (operator.is_, NoteSet(frozenset(map(Note, 'CDe'))), NoteSet.from_str('CDe')),
        (operator.is_, NoteSet(frozenset(map(Note, 'CDe')), root=Note('C')), NoteSet(frozenset(map(Note, 'CDe')), root=Note('C'))),
        (operator.is_, NoteSet(frozenset(map(Note, 'CDe')), root=Note('C')), NoteSet.from_str('CDe/C')),
        (operator.is_, NoteSet.from_str('CDe/C'), NoteSet.from_str('CDe/C')),
        (operator.is_not, NoteSet.from_str('CDe/C'), NoteSet.from_str('CDe/D')),
    ),
)
def test_noteset(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    'op, a, b', (
        (operator.is_, Scale.from_str('CdeFGab/C'), Scale.from_str('CdeFGab/C')),
        (operator.is_, Scale(frozenset(map(Note, 'CdeFGab')), root=Note('C')), Scale.from_str('CdeFGab/C')),
        (operator.is_not, Scale.from_str('CdeFGab/C'), Scale.from_str('CdeFGab/d')),
        (operator.is_, Scale.from_name('C', 'major'), Scale.from_name('C', 'major')),
        (operator.is_not, Scale.from_name('C', 'major'), Scale.from_name('D', 'major')),
        (operator.is_, Scale.from_name('C', 'major'), Scale.from_name(Note('C'), 'major')),
        (operator.is_, Scale.from_name('C', 'major'), Scale.from_str('CDEFGAB/C')),
    ),
)
def test_scale(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    'op, a, b', (
        (operator.is_, Chord(frozenset(map(Note, 'CEG')), root=Note('C')), Chord(frozenset(map(Note, 'CEG')), root=Note('C'))),
        (operator.is_, Chord(frozenset(map(Note, 'CEG')), root=Note('C')), Chord.from_str('CEG/C')),
        (operator.is_, Chord.from_str('CEG/C'), Chord.from_str('CEG/C')),
        (operator.is_not, Chord.from_str('CEG/C'), Chord.from_str('CeG/C')),
        (operator.is_not, Chord.from_str('CEG/C'), Chord.from_str('CEG/E')),
        (operator.is_, Chord.from_name('C', 'major'), Chord.from_name('C', 'major')),
        (operator.is_not, Chord.from_name('C', 'major'), Chord.from_name('D', 'major')),
        (operator.is_, Chord.from_name('C', 'major'), Chord.from_name(Note('C'), 'major')),
    ),
)
def test_chord(op, a, b):
    assert op(a, b)


def test_specific_chord():
    a = SpecificNote('C', 5)
    b = SpecificNote('E', 5)
    c = SpecificNote('G', 5)
    d = SpecificNote('C', 6)
    assert SpecificChord(frozenset({a, b, c})) is SpecificChord(frozenset({a, b, c}))
    assert SpecificChord(frozenset({a, b, c}), root='C') is SpecificChord(frozenset({a, b, c}), root=Note('C'))
    assert SpecificChord(frozenset({a, b, c}), root='C') is not SpecificChord(frozenset({a, b, d}), root=Note('C'))
    assert SpecificChord(frozenset({a, b, c}), root='C') is not SpecificChord(frozenset({a, b, c}), root=Note('E'))
    assert SpecificChord.from_str('C1_E1_G1/C') is SpecificChord.from_str('C1_E1_G1/C')
    assert SpecificChord.from_str('C1_E1_G1/C') is not SpecificChord.from_str('C1_E1_G1/E')
    assert SpecificChord.from_str('C1_E1_G1/C') is not SpecificChord.from_str('C1_e1_G1/C')


def test_progression():
    p0 = Progression((
        SpecificChord.from_str('G2_B2_e3'),
        SpecificChord.from_str('A2_C3_E3'),
        SpecificChord.from_str('B2_D3_f3'),
        SpecificChord.from_str('C3_E3_G3'),
    ))
    p1 = Progression((
        SpecificChord.from_str('G2_B2_e3'),
        SpecificChord.from_str('A2_C3_E3'),
        SpecificChord.from_str('B2_D3_f3'),
        SpecificChord.from_str('C3_E3_G3'),
    ))
    p2 = Progression((
        SpecificChord.from_str('C0_E0_a0'),
        SpecificChord.from_str('D0_F0_A0'),
        SpecificChord.from_str('E0_G0_B0'),
        SpecificChord.from_str('F0_A0_C1'),
    ))
    assert p0 is p1
    assert p0 is not p2


def test_cached_class():
    class K(Cached):
        def __init__(self, x):
            self.x = x

        def __bool__(self):
            """
            test walrus operator is properly used
            explicit `is not None` check should be used instead of `if cached := cache.get(key):`
            """
            return False

    assert K(1) is K(1)
    assert K(1) is not K(2)

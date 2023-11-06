import operator

import pytest
from musiclib.interval import AbstractInterval
from musiclib.intervalset import IntervalSet
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noteset import NoteSet
from musiclib.noteset import SpecificNoteSet
from musiclib.progression import Progression
from musiclib.scale import Scale
from musiclib.util.cache import Cached


@pytest.mark.parametrize(
    ('op', 'a', 'b'), [
        (operator.is_, Note('A'), Note('A')),
        (operator.is_not, Note('A'), Note('B')),
    ],
)
def test_note(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    ('op', 'a', 'b'), [
        (operator.is_, SpecificNote('C', 1), SpecificNote('C', 1)),
        (operator.is_not, SpecificNote('C', 1), SpecificNote('C', 2)),
        (operator.is_, SpecificNote('C', 1), SpecificNote(Note('C'), 1)),
    ],
)
def test_specific_note(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    ('op', 'a', 'b'), [
        (operator.is_, NoteSet(frozenset(map(Note, 'CDe'))), NoteSet(frozenset(map(Note, 'CDe')))),
        (operator.is_, NoteSet(frozenset(map(Note, 'CDe'))), NoteSet.from_str('CDe')),
    ],
)
def test_noteset(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    ('op', 'a', 'b'), [
        (operator.is_, AbstractInterval(10), AbstractInterval.from_str('A')),
        (operator.is_not, AbstractInterval(10), AbstractInterval(11)),
    ],
)
def test_abstract_interval(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    ('op', 'a', 'b'), [
        (operator.is_, IntervalSet(frozenset(map(AbstractInterval, {0, 4, 7}))), IntervalSet.from_name('major_0')),
        (operator.is_, IntervalSet(frozenset(map(AbstractInterval, {0, 4, 7}))), IntervalSet.from_bits('100010010000')),
        (operator.is_, IntervalSet(frozenset(map(AbstractInterval, {0, 4, 7}))), IntervalSet.from_base12(frozenset({'0', '4', '7'}))),
        (operator.is_not, IntervalSet(frozenset(map(AbstractInterval, {0, 4, 7}))), IntervalSet(frozenset(map(AbstractInterval, frozenset({0, 3, 7}))))),
    ],
)
def test_intervalset(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    ('op', 'a', 'b'), [
        (operator.is_, Scale.from_str('CdeFGab/C'), Scale.from_str('CdeFGab/C')),
        (operator.is_, Scale(Note('C'), IntervalSet(frozenset(map(AbstractInterval, {0, 1, 3, 5, 7, 8, 10})))), Scale.from_notes(Note('C'), frozenset(map(Note, 'CdeFGab')))),
        (operator.is_, Scale(Note('C'), IntervalSet(frozenset(map(AbstractInterval, {0, 1, 3, 5, 7, 8, 10})))), Scale.from_str('CdeFGab/C')),
        (operator.is_, Scale.from_notes(Note('C'), frozenset(map(Note, 'CEG'))), Scale.from_str('CEG/C')),
        (operator.is_, Scale.from_notes(Note('C'), frozenset(map(Note, 'CEG'))), Scale.from_notes(Note('C'), frozenset(map(Note, 'CEG')))),
        (operator.is_not, Scale.from_str('CdeFGab/C'), Scale.from_str('CdeFGab/d')),
        (operator.is_, Scale.from_name('C', 'major'), Scale.from_name('C', 'major')),
        (operator.is_not, Scale.from_name('C', 'major'), Scale.from_name('D', 'major')),
        (operator.is_, Scale.from_name('C', 'major'), Scale.from_name(Note('C'), 'major')),
        (operator.is_, Scale.from_name('C', 'major'), Scale.from_str('CDEFGAB/C')),
        (operator.is_, Scale.from_name('C', 'dim7_0'), Scale.from_name('C', 'dim7_1')),
        (operator.is_not, Scale.from_str('CEG/C'), Scale.from_str('CeG/C')),
        (operator.is_not, Scale.from_str('CEG/C'), Scale.from_str('CEG/E')),
    ],
)
def test_scale(op, a, b):
    assert op(a, b)


def test_specificnoteset():
    a = SpecificNote('C', 5)
    b = SpecificNote('E', 5)
    c = SpecificNote('G', 5)
    d = SpecificNote('C', 6)
    assert SpecificNoteSet(frozenset({a, b, c})) is SpecificNoteSet(frozenset({a, b, c}))
    assert SpecificNoteSet(frozenset({a, b, c})) is not SpecificNoteSet(frozenset({a, b, d}))
    assert SpecificNoteSet.from_str('C1_E1_G1') is SpecificNoteSet.from_str('C1_E1_G1')
    assert SpecificNoteSet.from_str('C1_E1_G1') is not SpecificNoteSet.from_str('C1_e1_G1')


def test_progression():
    p0 = Progression((
        SpecificNoteSet.from_str('G2_B2_e3'),
        SpecificNoteSet.from_str('A2_C3_E3'),
        SpecificNoteSet.from_str('B2_D3_f3'),
        SpecificNoteSet.from_str('C3_E3_G3'),
    ))
    p1 = Progression((
        SpecificNoteSet.from_str('G2_B2_e3'),
        SpecificNoteSet.from_str('A2_C3_E3'),
        SpecificNoteSet.from_str('B2_D3_f3'),
        SpecificNoteSet.from_str('C3_E3_G3'),
    ))
    p2 = Progression((
        SpecificNoteSet.from_str('C0_E0_a0'),
        SpecificNoteSet.from_str('D0_F0_A0'),
        SpecificNoteSet.from_str('E0_G0_B0'),
        SpecificNoteSet.from_str('F0_A0_C1'),
    ))
    assert p0 is p1
    assert p0 is not p2


def test_cached_class():
    class K(Cached):
        def __init__(self, x: int) -> None:
            self.x = x

        def __bool__(self):
            """
            test walrus operator is properly used
            explicit `is not None` check should be used instead of `if cached := cache.get(key):`
            """
            return False

    assert K(1) is K(1)
    assert K(1) is not K(2)

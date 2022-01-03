import pytest

from musictools.note import Note
from musictools.note import SpecificNote
from musictools.scale import ComparedScales
from musictools.scale import Scale
from musictools.chord import Chord
from musictools.scale import parallel
from musictools.scale import relative



@pytest.mark.parametrize(('notes', 'name'), (
    ('CDEFGAB', 'major'),
    ('CdeFGab', 'phrygian'),
    ('DEFGAbC', 'minor'),
    ('bdefa', 'p_phrygian'),
))
def test_name(notes, name):
    root = notes[0]
    notes = frozenset(notes)
    assert Scale(notes, root).name == name
    assert Scale.from_name(root, name).notes == notes


def test_kind():
    assert Scale.from_name('C', 'major').kind == 'diatonic'


def test_equal():
    assert Scale.from_name('C', 'major') == Scale.from_name('C', 'major')
    assert Scale.from_name('C', 'major') == Scale.from_name(Note('C'), 'major')
    assert Scale.from_name(Note('C'), 'major') == Scale.from_name(Note('C'), 'major')
    assert Scale.from_name(Note('C'), 'major') != Scale.from_name(Note('E'), 'major')


@pytest.mark.parametrize(('notes', 'triads'), (
    ('CDEFGAB', 'CEG/C DFA/D EGB/E FAC/F GBD/G ACE/A BDF/B'),
    ('DEFGAbC', 'DFA/D EGb/E FAC/F GbD/G ACE/A bDF/b CEG/C'),
))
def test_scale_triads(notes, triads):
    assert Scale(frozenset(notes), notes[0]).triads == tuple(Chord.from_str(s) for s in triads.split())


def test_cache():
    assert Scale.from_name('C', 'major') is Scale.from_name('C', 'major')
    assert Scale.from_name('C', 'major') is not Scale.from_name('D', 'major')
    assert Scale.from_name('C', 'major') is Scale.from_name(Note('C'), 'major')


# def test_compared():
#     left = Scale('C', 'major')
#     right = Scale('A', 'minor')
#     assert ComparedScales(left, right).shared_notes == frozenset(left.notes)
#
#     right = Scale('C', 'mixolydian')
#     c = ComparedScales(left, right)
#     assert c.new_notes == frozenset({Note('b')})
#     assert c.del_notes == frozenset({Note('B')})
#
#
# def test_parallel():
#     a = Scale('C', 'major')
#     b = Scale('C', 'minor')
#     assert parallel(a) is b
#     assert parallel(b) is a
#     assert parallel(Scale('f', 'minor')) is Scale('f', 'major')
#
#
# def test_relative():
#     a = Scale('C', 'major')
#     b = Scale('A', 'minor')
#     c = Scale('f', 'minor')
#     d = Scale('A', 'major')
#     assert relative(a) is b
#     assert relative(b) is a
#     assert relative(c) is d
#     assert relative(d) is c

import pytest

from musictools.note import Note
from musictools.note import SpecificNote
from musictools.scale import ComparedScales
from musictools.scale import Scale
from musictools.chord import Chord
from musictools.scale import parallel
from musictools.scale import relative



@pytest.mark.parametrize(('notes', 'root', 'name'), (
    (frozenset('CDEFGAB'), 'C', 'major'),
    (frozenset('CdeFGab'), 'C', 'phrygian'),
    (frozenset('DEFGAbC'), 'D', 'minor'),
    (frozenset('bdefa'), 'b', 'p_phrygian'),
))
def test_name(notes, root, name):
    assert Scale(notes, root).name == name
    assert Scale.from_name(root, name).notes == notes


def test_kind():
    assert Scale.from_name('C', 'major').kind == 'diatonic'


def test_equal():
    assert Scale.from_name('C', 'major') == Scale.from_name('C', 'major')
    assert Scale.from_name('C', 'major') == Scale.from_name(Note('C'), 'major')
    assert Scale.from_name(Note('C'), 'major') == Scale.from_name(Note('C'), 'major')
    assert Scale.from_name(Note('C'), 'major') != Scale.from_name(Note('E'), 'major')


@pytest.mark.parametrize(('notes', 'root', 'triads'), (
    (frozenset('CDEFGAB'), 'C', 'CEG/C DFA/D EGB/E FAC/F GBD/G ACE/A BDF/B'),
    (frozenset('DEFGAbC'), 'D', 'DFA/D EGb/E FAC/F GbD/G ACE/A bDF/b CEG/C'),
))
def test_scale_triads(notes, root, triads):
    assert Scale(notes, root).triads == tuple(Chord.from_str(s) for s in triads.split())


@pytest.mark.xfail(reason='TODO')
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

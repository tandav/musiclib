import pytest

from musictools import config
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


@pytest.mark.parametrize('notes', ('CDEFGAB', 'BdeEfab', 'deFfabC'))
def test_note_scales(notes):
    assert Scale(frozenset(notes), notes[0]).note_scales == dict(zip(notes, config.diatonic))


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


def test_parallel():
    a = Scale.from_name('C', 'major')
    b = Scale.from_name('C', 'minor')
    assert parallel(a) is b
    assert parallel(b) is a
    assert parallel(Scale.from_name('f', 'minor')) is Scale.from_name('f', 'major')


def test_relative():
    a = Scale.from_name('C', 'major')
    b = Scale.from_name('A', 'minor')
    c = Scale.from_name('f', 'minor')
    d = Scale.from_name('A', 'major')
    assert relative(a) is b
    assert relative(b) is a
    assert relative(c) is d
    assert relative(d) is c

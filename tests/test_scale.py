import pytest

from musictools.note import Note
from musictools.note import SpecificNote
from musictools.scale import ComparedScales
from musictools.scale import Scale
from musictools.scale import parallel
from musictools.scale import relative


def test_kind():
    assert Scale('C', 'major').kind == 'diatonic'


def test_equal():
    assert Scale('C', 'major') == Scale('C', 'major')
    assert Scale('C', 'major') == Scale(Note('C'), 'major')
    assert Scale(Note('C'), 'major') == Scale(Note('C'), 'major')
    assert Scale(Note('C'), 'major') != Scale(Note('E'), 'major')


def test_cache():
    assert Scale('C', 'major') is Scale('C', 'major')
    assert Scale('C', 'major') is not Scale('D', 'major')
    assert Scale('C', 'major') is Scale(Note('C'), 'major')


@pytest.mark.parametrize(
    ('scale_name', 'expected_notes'),
    (('major', 'CDEFGAB'), ('phrygian', 'CdeFGab')),
)
def test_notes(scale_name, expected_notes):
    assert ''.join(note.name for note in Scale('C', scale_name).notes) == expected_notes


@pytest.mark.parametrize(
    ('scale', 'note', 'steps', 'result'), (
    (Scale('C', 'major'), Note('C'), 3, Note('F')),
    (Scale('C', 'major'), Note('C'), -2, Note('A')),
    (Scale('D', 'minor'), Note('A'), 1, Note('b')),
    (Scale('D', 'minor'), Note('A'), 0, Note('A')),
    (Scale('C', 'major'), SpecificNote('C', 1), 3, SpecificNote('F', 1)),
    (Scale('C', 'major'), SpecificNote('C', 1), -2, SpecificNote('A', 0)),
    (Scale('C', 'minor'), SpecificNote('G', 5), -22, SpecificNote('F', 2)),
    (Scale('D', 'minor'), SpecificNote('A', 1), 8, SpecificNote('b', 2)),
    (Scale('D', 'minor'), SpecificNote('A', 1), 0, SpecificNote('A', 1)),
    (Scale('D', 'minor'), SpecificNote('A', 2), -7, SpecificNote('A', 1)),
    ))
def test_add_note(scale, note, steps, result):
    assert scale.add_note(note, steps) == result


def test_compared():
    left = Scale('C', 'major')
    right = Scale('A', 'minor')
    assert ComparedScales(left, right).shared_notes == frozenset(left.notes)

    right = Scale('C', 'mixolydian')
    c = ComparedScales(left, right)
    assert c.new_notes == frozenset({Note('b')})
    assert c.del_notes == frozenset({Note('B')})


def test_parallel():
    a = Scale('C', 'major')
    b = Scale('C', 'minor')
    assert parallel(a) is b
    assert parallel(b) is a
    assert parallel(Scale('f', 'minor')) is Scale('f', 'major')


def test_relative():
    a = Scale('C', 'major')
    b = Scale('A', 'minor')
    c = Scale('f', 'minor')
    d = Scale('A', 'major')
    assert relative(a) is b
    assert relative(b) is a
    assert relative(c) is d
    assert relative(d) is c
@pytest.mark.parametrize(('notes', 'root', 'name'), (
    (frozenset('CDEFGAB'), 'C', 'major'),
    (frozenset('CdeFGab'), 'C', 'phrygian'),
    (frozenset('DEFGAbC'), 'D', 'minor'),
    (frozenset('bdefa'), 'b', 'p_phrygian'),
))
def test_name(notes, root, name):
    assert Scale(notes, root).name == name

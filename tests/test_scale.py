import pytest

from musictools.note import Note
from musictools.scale import ComparedScales
from musictools.scale import Scale


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


def test_compared():
    left = Scale('C', 'major')
    right = Scale('A', 'minor')
    assert ComparedScales(left, right).shared_notes == frozenset(left.notes)

    right = Scale('C', 'mixolydian')
    c = ComparedScales(left, right)
    assert c.new_notes == frozenset({Note('b')})
    assert c.del_notes == frozenset({Note('B')})

from piano_scales.scale import Scale
from piano_scales.note import Note


def test_kind():
    assert Scale('C', 'major').kind == 'diatonic'


def test_equal():
    assert Scale('C', 'major') == Scale('C', 'major')
    assert Scale('C', 'major') == Scale(Note('C'), 'major')
    assert Scale(Note('C'), 'major') == Scale(Note('C'), 'major')
    assert Scale(Note('C'), 'major') != Scale(Note('E'), 'major')


def test_notes():
    assert ''.join(note.name for note in Scale('C', 'major').notes) == 'CDEFGAB'
    assert ''.join(note.name for note in Scale('C', 'phrygian').notes) == 'CdeFGab'

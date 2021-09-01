from piano_scales.scale import Scale


def test_kind():
    s = Scale('C', 'major')
    assert s.kind == 'diatonic'


def test_notes():
    s = Scale('C', 'major')
    assert ''.join(note.name for note in s.notes) == 'CDEFGAB'

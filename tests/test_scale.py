import pytest

from musictool import config
from musictool.chord import Chord
from musictool.note import Note
from musictool.scale import ComparedScales
from musictool.scale import Scale
from musictool.scale import parallel
from musictool.scale import relative


@pytest.mark.parametrize('notes, name', (
    ('CDEFGAB', 'major'),
    ('CdeFGab', 'phrygian'),
    ('DEFGAbC', 'minor'),
    ('bdefa', 'p_phrygian'),
))
def test_name(notes, name):
    root = notes[0]
    notes = frozenset(notes)
    assert Scale(notes, root=root).name == name
    assert Scale.from_name(root, name).notes == notes


def test_kind():
    s = Scale.from_name('C', 'major')
    assert (
        s.kind == 'diatonic' and
        {'note_colors', 'note_scales', 'triads', 'sevenths', 'ninths', 'notes_to_triad_root'} <= vars(s).keys()
    )
    s = Scale.from_name('C', 'p_major')
    assert (
        s.kind == 'pentatonic' and
        {'note_colors', 'note_scales'} <= vars(s).keys() and
        len({'triads', 'sevenths', 'ninths', 'notes_to_triad_root'} & vars(s).keys()) == 0
    )
    s = Scale(frozenset('Cde'), root='C')
    assert (
        s.kind is None and
        len({'note_colors', 'note_scales', 'triads', 'sevenths', 'ninths', 'notes_to_triad_root'} & vars(s).keys()) == 0
    )


def test_equal():
    assert Scale.from_name('C', 'major') == Scale.from_name('C', 'major')
    assert Scale.from_name('C', 'major') == Scale.from_name(Note('C'), 'major')
    assert Scale.from_name(Note('C'), 'major') == Scale.from_name(Note('C'), 'major')
    assert Scale.from_name(Note('C'), 'major') != Scale.from_name(Note('E'), 'major')


@pytest.mark.parametrize('notes, name, nths', (
    ('CDEFGAB', 'triads', 'CEG/C DFA/D EGB/E FAC/F GBD/G ACE/A BDF/B'),
    ('DEFGAbC', 'triads', 'DFA/D EGb/E FAC/F GbD/G ACE/A bDF/b CEG/C'),
    ('CDEFGAB', 'sevenths', 'CEGB/C DFAC/D EGBD/E FACE/F GBDF/G ACEG/A BDFA/B'),
    ('DEFGAbC', 'sevenths', 'DFAC/D EGbD/E FACE/F GbDF/G ACEG/A bDFA/b CEGb/C'),
    ('CDEFGAB', 'ninths', 'CEGBD/C DFACE/D EGBDF/E FACEG/F GBDFA/G ACEGB/A BDFAC/B'),
    ('DEFGAbC', 'ninths', 'DFACE/D EGbDF/E FACEG/F GbDFA/G ACEGb/A bDFAC/b CEGbD/C'),
))
def test_nths(notes, name, nths):
    assert getattr(Scale(frozenset(notes), root=notes[0]), name) == tuple(Chord.from_str(s) for s in nths.split())


def test_notes_to_triad_root():
    assert Scale(frozenset('DEFGAbC'), root='D').notes_to_triad_root[frozenset('GbD')] == 'G'


@pytest.mark.parametrize('notes', ('CDEFGAB', 'BdeEfab', 'deFfabC'))
def test_note_scales(notes):
    assert Scale(frozenset(notes), root=notes[0]).note_scales == dict(zip(notes, config.diatonic))


def test_compared():
    left = Scale.from_name('C', 'major')
    right = Scale.from_name('A', 'minor')
    assert ComparedScales(left, right).shared_notes == frozenset(left.notes)

    right = Scale.from_name('C', 'mixolydian')
    c = ComparedScales(left, right)
    assert c.new_notes == frozenset({Note('b')})
    assert c.del_notes == frozenset({Note('B')})


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


@pytest.fixture(params=(Scale.from_name('C', 'major'), Scale.from_name('A', 'major')))
def scale(request):
    yield request.param


def test_svg_scale(scale):
    scale.to_piano_image()


def test_svg_compared_scale(scale):
    ComparedScales(scale, Scale.from_name('f', 'phrygian')).to_piano_image()

import operator

import pytest
from musiclib import config
from musiclib.note import Note
from musiclib.scale import ComparedScales
from musiclib.scale import Scale



@pytest.mark.parametrize(
    ('root', 'notes', 'expected'), [
        (Note('C'), frozenset(map(Note, 'CEG')), Scale(Note('C'), frozenset({0, 4, 7}))),
        (Note('E'), frozenset(map(Note, 'AB')), ValueError),
    ],
)
def test_from_notes(root, notes, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            Scale.from_notes(root, notes)
        return
    assert Scale.from_notes(root, notes) is expected


@pytest.mark.parametrize(
    ('scale', 'expected'), [
        (Scale.from_notes(Note('B'), frozenset(map(Note, 'BDF'))), 'BDF/B'),
        (Scale.from_notes(Note('B'), frozenset(map(Note, 'DGBFCEA'))), 'BCDEFGA/B'),
    ],
)
def test_notes_str_sort_2_octaves(scale, expected):
    assert scale.notes_str == expected


@pytest.mark.parametrize(
    ('string', 'expected'), [
        ('CDEFGAB/C', Scale.from_notes(Note('C'), frozenset(map(Note, 'CDEFGAB')))),
        ('CdeFGab/e', Scale.from_notes(Note('e'), frozenset(map(Note, 'CdeFGab')))),
        ('CEG/C', Scale.from_notes(Note('C'), frozenset(map(Note, 'CEG')))),
        ('fa/a', Scale.from_notes(Note('a'), frozenset(map(Note, 'fa')))),
    ],
)
def test_from_str(string, expected):
    assert Scale.from_str(string) == expected

@pytest.mark.parametrize('string', [
    '',
    'CDE',
])
def test_from_str_validation(string):
    with pytest.raises(ValueError):
        Scale.from_str(string)


@pytest.mark.parametrize(
    ('root', 'name', 'expected'), [
        (Note('C'), 'major', Scale.from_str('CDEFGAB/C')),
        (Note('C'), 'minor', Scale.from_str('CDeFGab/C')),
        (Note('C'), 'major_0', Scale.from_str('CEG/C')),
        (Note('C'), '7_0', Scale.from_str('CEGb/C')),
    ],
)
def test_from_name(root, name, expected):
    assert Scale.from_name(root, name) == expected


@pytest.mark.parametrize(
    ('scale', 'intervals'), [
        (Scale.from_str('CDEFGAB/C'), (0, 2, 4, 5, 7, 9, 11)),
        (Scale.from_str('DeFGAbC/D'), (0, 1, 3, 5, 7, 8, 10)),
    ],
)
def test_intervals(scale, intervals):
    assert scale.intervals_ascending == intervals
    assert scale.intervals == frozenset(intervals)


@pytest.mark.parametrize(
    ('scale', 'note_to_interval'), [
        (Scale.from_str('CDE/C'), {Note('C'): 0, Note('D'): 2, Note('E'): 4}),
    ],
)
def test_note_to_interval(scale, note_to_interval):
    assert scale.note_to_interval == note_to_interval


@pytest.mark.parametrize(
    ('notes', 'bits'), [
        ('CDEFGAB/C', '101011010101'),
        ('dfb/d', '100001000100'),
    ],
)
def test_bits(notes, bits):
    assert Scale.from_str(notes).bits == bits


@pytest.mark.parametrize(
    ('scale', 'bits'), [
        (Scale.from_str('CDE/D'), (1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0)),
        (Scale.from_str('df/f'), (0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)),
    ],
)
def test_bits_chromatic_notes(scale, bits):
    assert scale.bits_chromatic_notes == bits



@pytest.mark.parametrize(
    ('scale', 'note', 'expected'), [
        ('CDEFGAB/C', 'A', 'ABdDEfa/A'),
        ('CdeFGab/e', 'D', 'DEfGABC/D'),
        ('Cd/C', 'd', 'dD/d'),
    ],
)
def test_transpose_to_note(scale, note, expected):
    assert Scale.from_str(scale).transpose_to_note(Note(note)) is Scale.from_str(expected)


@pytest.mark.parametrize(
    ('notes', 'name'), [
        ('CDEFGAB', 'major'),
        ('CdeFGab', 'phrygian'),
        ('DEFGAbC', 'minor'),
        ('bdefa', 'p_phrygian'),
    ],
)
def test_name(notes, name):
    root = Note(notes[0])
    notes = frozenset(map(Note, notes))
    assert Scale.from_notes(root, notes).name == name
    assert Scale.from_name(root, name).notes == notes


@pytest.mark.parametrize('scale, expected', [
    (Scale.from_name('C', 'major'), 'natural'),
    (Scale.from_name('C', 'p_major'), 'pentatonic'),
    # chords
    (Scale.from_name('C', 'major_0'), 'major'),
    (Scale.from_name('C', 'major_1'), 'major'),
    (Scale.from_name('C', 'major_2'), 'major'),
    (Scale.from_name('C', 'minor_0'), 'minor'),
    (Scale.from_name('C', 'minor_1'), 'minor'),
    (Scale.from_name('C', 'minor_2'), 'minor'),
    (Scale.from_name('C', '7_0'), '7'),
    (Scale.from_name('C', '7_1'), '7'),
    (Scale.from_name('C', '7_2'), '7'),
    (Scale.from_name('C', '7_3'), '7'),
    (Scale.from_name('C', 'dim7_0'), 'dim7'),
    (Scale.from_name('C', 'dim7_1'), 'dim7'),
    (Scale.from_name('C', 'dim7_2'), 'dim7'),
    (Scale.from_name('C', 'dim7_3'), 'dim7'),
])
def test_kind(scale, expected):
    assert scale.kind == expected


@pytest.mark.parametrize(
    ('op', 'a', 'b'), [
        (operator.eq, Scale.from_name('C', 'major'), Scale.from_name('C', 'major')),
        (operator.eq, Scale.from_name('C', 'major'), Scale.from_name(Note('C'), 'major')),
        (operator.eq, Scale.from_name(Note('C'), 'major'), Scale.from_name(Note('C'), 'major')),
        (operator.ne, Scale.from_name(Note('C'), 'major'), Scale.from_name(Note('E'), 'major')),
    ],
)
def test_equal(op, a, b):
    assert op(a, b)
    if op is operator.eq:
        assert operator.is_(a, b)


@pytest.mark.parametrize(
    ('notes', 'name', 'nths'), [
        ('CDEFGAB', 'triads', 'CEG/C DFA/D EGB/E FAC/F GBD/G ACE/A BDF/B'),
        ('DEFGAbC', 'triads', 'DFA/D EGb/E FAC/F GbD/G ACE/A bDF/b CEG/C'),
        ('CDEFGAB', 'sixths', 'CEGA/C DFAB/D EGBC/E FACD/F GBDE/G ACEF/A BDFG/B'),
        ('CDEFGAB', 'sevenths', 'CEGB/C DFAC/D EGBD/E FACE/F GBDF/G ACEG/A BDFA/B'),
        ('DEFGAbC', 'sevenths', 'DFAC/D EGbD/E FACE/F GbDF/G ACEG/A bDFA/b CEGb/C'),
        ('CDEFGAB', 'ninths', 'CEGBD/C DFACE/D EGBDF/E FACEG/F GBDFA/G ACEGB/A BDFAC/B'),
        ('DEFGAbC', 'ninths', 'DFACE/D EGbDF/E FACEG/F GbDFA/G ACEGb/A bDFAC/b CEGbD/C'),
    ],
)
def test_nths(notes, name, nths):
    assert Scale.from_str(f'{notes}/{notes[0]}').nths(config.nths[name]) == tuple(Scale.from_str(s) for s in nths.split())


@pytest.mark.parametrize('notes', ['CDEFGAB', 'BdeEfab', 'deFfabC'])
def test_note_scales(notes):
    assert Scale.from_str(f'{notes}/{notes[0]}').note_scales == dict(zip(notes, config.scale_order['natural'], strict=True))


def test_compared():
    left = Scale.from_name('C', 'major')
    right = Scale.from_name('A', 'minor')
    assert ComparedScales(left, right).shared_notes == frozenset(left.notes)

    right = Scale.from_name('C', 'mixolydian')
    c = ComparedScales(left, right)
    assert c.new_notes == frozenset({Note('b')})
    assert c.del_notes == frozenset({Note('B')})

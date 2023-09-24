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
    assert str(scale) == expected


@pytest.mark.parametrize(
    ('string', 'expected'), [
        ('CDEFGAB/C', Scale.from_notes(Note('C'), frozenset(map(Note, 'CDEFGAB')))),
        ('CdeFGab/e', Scale.from_notes(Note('e'), frozenset(map(Note, 'CdeFGab')))),
        ('CEG/C', Scale.from_notes(Note('C'), frozenset(map(Note, 'CEG')))),
        ('fa/a', Scale.from_notes(Note('a'), frozenset(map(Note, 'fa')))),
    ],
)
def test_from_str(string, expected):
    assert Scale.from_str(string) is expected
    assert Scale.from_str(str(expected)) is expected


@pytest.mark.parametrize(
    ('scale', 's', 'r', 'str_names'), [
        (Scale.from_str('CDEFGAB/C'), 'CDEFGAB/C', "Scale(Note('C'), frozenset({0, 2, 4, 5, 7, 9, 11}))", 'C major'),
        (Scale.from_str('CEa/C'), 'CEa/C', "Scale(Note('C'), frozenset({0, 8, 4}))", 'C aug_0 aug_1 aug_2'),
        (Scale.from_str('DFaC/D'), 'DFaC/D', "Scale(Note('D'), frozenset({0, 10, 3, 6}))", 'D half-dim7_0 m6_3'),
    ],
)
def test_str_repr(scale, s, r, str_names):
    assert str(scale) == s
    assert repr(scale) == r
    assert scale.str_names == str_names


@pytest.mark.parametrize(
    'string', [
        '',
        'CDE',
    ],
)
def test_from_str_validation(string):
    with pytest.raises(ValueError):
        Scale.from_str(string)


@pytest.mark.parametrize(
    ('root', 'name', 'expected'), [
        (Note('C'), 'major', Scale.from_str('CDEFGAB/C')),
        (Note('C'), 'minor', Scale.from_str('CDeFGab/C')),
        (Note('C'), 'major_0', Scale.from_str('CEG/C')),
        (Note('C'), '7_0', Scale.from_str('CEGb/C')),
        (Note('d'), '7_0', Scale.from_str('dFaB/d')),
    ],
)
def test_from_name(root, name, expected):
    assert Scale.from_name(root, name) == expected


@pytest.mark.parametrize(
    ('scale', 'intervals'), [
        (Scale.from_str('CDEFGAB/C'), (0, 2, 4, 5, 7, 9, 11)),
        (Scale.from_str('CEG/C'), (0, 4, 7)),
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
    ('scale', 'names'), [
        (Scale.from_str('CDEFGAB/C'), frozenset({'major'})),
        (Scale.from_str('CdeFGab/C'), frozenset({'phrygian'})),
        (Scale.from_str('DEFGAbC/D'), frozenset({'minor'})),
        (Scale.from_str('bdefa/b'), frozenset({'p_phrygian'})),
        (Scale.from_str('CEG/C'), frozenset({'major_0'})),
        (Scale.from_str('BDF/B'), frozenset({'dim_0'})),
        (Scale.from_str('CefA/C'), frozenset({'dim7_0', 'dim7_1', 'dim7_2', 'dim7_3'})),
        (Scale.from_str('CEa/C'), frozenset({'aug_0', 'aug_1', 'aug_2'})),
        (Scale.from_str('DFaC/D'), frozenset({'m6_3', 'half-dim7_0'})),
        (Scale(Note('C'), frozenset({0, 3, 7, 10})), frozenset({'6_3', 'min7_0'})),
        (Scale(Note('C'), frozenset({0, 4, 7, 9})), frozenset({'6_0', 'min7_1'})),
        (Scale(Note('C'), frozenset({0, 3, 5, 8})), frozenset({'6_1', 'min7_2'})),
        (Scale(Note('C'), frozenset({0, 2, 5, 9})), frozenset({'6_2', 'min7_3'})),
        (Scale(Note('C'), frozenset({0, 3, 6, 10})), frozenset({'half-dim7_0', 'm6_3'})),
        (Scale(Note('C'), frozenset({0, 3, 7, 9})), frozenset({'half-dim7_1', 'm6_0'})),
        (Scale(Note('C'), frozenset({0, 4, 6, 9})), frozenset({'half-dim7_2', 'm6_1'})),
        (Scale(Note('C'), frozenset({0, 2, 5, 8})), frozenset({'half-dim7_3', 'm6_2'})),
        (Scale(Note('C'), frozenset({0, 3, 6, 9})), frozenset({'dim7_0', 'dim7_1', 'dim7_2', 'dim7_3'})),
        (Scale(Note('C'), frozenset({0, 4, 8})), frozenset({'aug_0', 'aug_1', 'aug_2'})),
        (Scale(Note('C'), frozenset({0, 2, 7})), frozenset({'sus2_0', 'sus4_1'})),
        (Scale(Note('C'), frozenset({0, 5, 10})), frozenset({'sus2_1', 'sus4_2'})),
        (Scale(Note('C'), frozenset({0, 5, 7})), frozenset({'sus2_2', 'sus4_0'})),
    ],
)
def test_names(scale, names):
    assert scale.names == names
    for name in names:
        assert Scale.from_name(scale.root, name).notes == scale.notes


@pytest.mark.parametrize(
    ('scale', 'expected'), [
        (Scale.from_name('C', 'major'), {'major': 'natural'}),
        (Scale.from_name('C', 'p_major'), {'p_major': 'pentatonic'}),
        # chords
        (Scale.from_name('C', 'major_0'), {'major_0': 'major'}),
        (Scale.from_name('C', 'major_1'), {'major_1': 'major'}),
        (Scale.from_name('C', 'major_2'), {'major_2': 'major'}),
        (Scale.from_name('C', '7_0'), {'7_0': '7'}),
        (Scale.from_name('C', '7_1'), {'7_1': '7'}),
        (Scale.from_name('C', '7_2'), {'7_2': '7'}),
        (Scale.from_name('C', '7_3'), {'7_3': '7'}),
        (Scale.from_name('C', 'dim7_0'), {'dim7_0': 'dim7', 'dim7_1': 'dim7', 'dim7_2': 'dim7', 'dim7_3': 'dim7'}),
        (Scale.from_name('C', 'dim7_1'), {'dim7_0': 'dim7', 'dim7_1': 'dim7', 'dim7_2': 'dim7', 'dim7_3': 'dim7'}),
        (Scale.from_name('C', 'dim7_2'), {'dim7_0': 'dim7', 'dim7_1': 'dim7', 'dim7_2': 'dim7', 'dim7_3': 'dim7'}),
        (Scale.from_name('C', 'dim7_3'), {'dim7_0': 'dim7', 'dim7_1': 'dim7', 'dim7_2': 'dim7', 'dim7_3': 'dim7'}),
        (Scale.from_str('CEa/C'), {'aug_1': 'aug', 'aug_2': 'aug', 'aug_0': 'aug'}),
        (Scale.from_str('DFaC/D'), {'half-dim7_0': 'half-dim7', 'm6_3': 'm6'}),
        (Scale(Note('C'), frozenset({0, 3, 7, 10})), {'min7_0': 'min7', '6_3': '6'}),
        (Scale(Note('C'), frozenset({0, 4, 7, 9})), {'min7_1': 'min7', '6_0': '6'}),
        (Scale(Note('C'), frozenset({0, 3, 5, 8})), {'6_1': '6', 'min7_2': 'min7'}),
        (Scale(Note('C'), frozenset({0, 2, 5, 9})), {'min7_3': 'min7', '6_2': '6'}),
        (Scale(Note('C'), frozenset({0, 3, 6, 10})), {'half-dim7_0': 'half-dim7', 'm6_3': 'm6'}),
        (Scale(Note('C'), frozenset({0, 3, 7, 9})), {'m6_0': 'm6', 'half-dim7_1': 'half-dim7'}),
        (Scale(Note('C'), frozenset({0, 4, 6, 9})), {'half-dim7_2': 'half-dim7', 'm6_1': 'm6'}),
        (Scale(Note('C'), frozenset({0, 2, 5, 8})), {'m6_2': 'm6', 'half-dim7_3': 'half-dim7'}),
        (Scale(Note('C'), frozenset({0, 3, 6, 9})), {'dim7_0': 'dim7', 'dim7_2': 'dim7', 'dim7_3': 'dim7', 'dim7_1': 'dim7'}),
        (Scale(Note('C'), frozenset({0, 4, 8})), {'aug_1': 'aug', 'aug_2': 'aug', 'aug_0': 'aug'}),
        (Scale(Note('C'), frozenset({0, 2, 7})), {'sus2_0': 'sus2', 'sus4_1': 'sus4'}),
        (Scale(Note('C'), frozenset({0, 5, 10})), {'sus4_2': 'sus4', 'sus2_1': 'sus2'}),
        (Scale(Note('C'), frozenset({0, 5, 7})), {'sus2_2': 'sus2', 'sus4_0': 'sus4'}),
    ],
)
def test_name_kinds(scale, expected):
    assert scale.name_kinds == expected


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
    assert Scale.from_str(f'{notes}/{notes[0]}').note_scales == {'natural': dict(zip(map(Note, notes), config.scale_order['natural'], strict=True))}


def test_compared():
    left = Scale.from_name('C', 'major')
    right = Scale.from_name('A', 'minor')
    assert ComparedScales(left, right).shared_notes == frozenset(left.notes)

    right = Scale.from_name('C', 'mixolydian')
    c = ComparedScales(left, right)
    assert c.new_notes == frozenset({Note('b')})
    assert c.del_notes == frozenset({Note('B')})

import itertools
from collections.abc import Iterable
from collections.abc import Sequence

import pytest

from musictool import config
from musictool.chord import Chord
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noteset import NoteRange
from musictool.noteset import NoteSet
from musictool.noteset import bits_to_intervals
from musictool.noteset import intervals_to_bits
from musictool.scale import Scale
from musictool.scale import all_scales


@pytest.mark.parametrize('bits, intervals', (
    ('101011010101', frozenset({2, 4, 5, 7, 9, 11})),
    ('110101101010', frozenset({1, 3, 5, 6, 8, 10})),
    ('101001010100', frozenset({2, 5, 7, 9})),
    ('101101010010', frozenset({2, 3, 5, 7, 10})),
))
def test_bits_intervals(bits, intervals):
    assert bits_to_intervals(bits) == intervals
    assert intervals_to_bits(intervals) == bits


@pytest.mark.parametrize('noteset, intervals', (
    (NoteSet(frozenset('CDEFGAB'), root='C'), (0, 2, 4, 5, 7, 9, 11)),
    (NoteSet(frozenset('DeFGAbC'), root='D'), (0, 1, 3, 5, 7, 8, 10)),
))
def test_intervals(noteset, intervals):
    assert noteset.intervals_ascending == intervals
    assert noteset.intervals == frozenset(intervals[1:])


@pytest.mark.parametrize('noteset, increments, decrements', (
    (NoteSet(frozenset('DEFGABC')), {'D': 2, 'E': 1, 'F': 2, 'G': 2, 'A': 2, 'B': 1, 'C': 2}, {'D': -2, 'E': -2, 'F': -1, 'G': -2, 'A': -2, 'B': -2, 'C': -1}),
    (NoteSet(frozenset('dDFfaAB')), {'d': 1, 'D': 3, 'F': 1, 'f': 2, 'a': 1, 'A': 2, 'B': 2}, {'d': -2, 'D': -1, 'F': -3, 'f': -1, 'a': -2, 'A': -1, 'B': -2}),
    (NoteSet(frozenset('bBCd')), {'b': 1, 'B': 1, 'C': 1, 'd': 9}, {'b': -9, 'B': -1, 'C': -1, 'd': -1}),
))
def test_increments_decrements(noteset, increments, decrements):
    assert noteset.increments == increments
    assert noteset.decrements == decrements


@pytest.mark.parametrize('notes, root, bits', (
    ('CDEFGAB', 'C', '101011010101'),
    ('dfb', 'd', '100001000100'),
))
def test_bits(notes, root, bits):
    assert NoteSet(frozenset(notes), root=root).bits == bits


def test_empty():
    with pytest.raises(ValueError): NoteSet(frozenset())


@pytest.mark.parametrize('value', ('CDE', set('CDE'), tuple('CDE'), list('CDE')))
def test_notes_type_is_frozenset(value):
    with pytest.raises(TypeError): NoteSet(value)


def test_contains():
    assert 'C' in NoteSet(frozenset('C'))
    assert 'C' not in NoteSet(frozenset('D'))
    assert frozenset('CD') <= NoteSet(frozenset('CDE'))
    assert frozenset('CDE') <= NoteSet(frozenset('CDE'))
    assert not frozenset('CDEF') <= NoteSet(frozenset('CDE'))
    assert NoteSet(frozenset('CD')) <= frozenset('CDE')
    assert NoteSet(frozenset('CDE')) <= frozenset('CDE')
    assert not NoteSet(frozenset('CDEF')) <= frozenset('CDE')


def test_root_validation():
    with pytest.raises(KeyError): NoteSet(frozenset('AB'), root='E')


def test_note_i():
    fs = frozenset(map(Note, 'CDEfGaB'))
    noteset = NoteSet(fs)
    assert fs == noteset.note_i.keys()
    assert noteset.note_i[Note('C')] == 0
    assert noteset.note_i[Note('B')] == 6
    assert noteset.note_i[Note('f')] == 3
    assert noteset.note_i[Note('G')] == 4


@pytest.mark.parametrize('string, expected', (
    ('CDEFGAB/C', NoteSet(frozenset('CDEFGAB'), root='C')),
    ('CDEFGAB', NoteSet(frozenset('CDEFGAB'))),
    ('CdeFGab/e', NoteSet(frozenset('CdeFGab'), root='e')),
    ('CEG/C', NoteSet(frozenset('CEG'), root='C')),
    ('fa/a', NoteSet(frozenset('fa'), root='a')),
))
def test_from_str(string, expected):
    assert NoteSet.from_str(string) == expected


@pytest.mark.parametrize('intervals, root, expected', (
    (frozenset({4, 7}), 'C', NoteSet(frozenset('CEG'), root='C')),
    (frozenset({1, 3, 5, 7, 8, 10}), 'E', NoteSet(frozenset('CDEFGAB'), root='E')),
    (frozenset({2, 3, 5, 7, 9, 10}), 'f', NoteSet(frozenset('faABdeE'), root='f')),
))
def test_from_intervals(root, intervals, expected):
    assert NoteSet.from_intervals(intervals, root) is expected


def test_childs_names_unreachable():
    with pytest.raises(KeyError): NoteSet.from_name('C', 'major')  # test that Scale names are unreachable
    with pytest.raises(KeyError): NoteSet.from_name('e', 'aug')  # test that Chord names are unreachable


@pytest.mark.parametrize('noteset, notes_octave_fit', (
    (NoteSet(frozenset('efGd')), 'defG'),
    (NoteSet(frozenset('efGd'), root='e'), 'defG'),
    (NoteSet(frozenset('FGbBCd'), root='F'), 'CdFGbB')
))
def test_notes_octave_fit(noteset, notes_octave_fit):
    assert noteset.notes_octave_fit == tuple(notes_octave_fit)


@pytest.mark.parametrize('noteset, note, steps, result', (
    (NoteSet(frozenset('CDEFGAB')), Note('C'), 3, 'F'),
    (NoteSet(frozenset('CDEFGAB')), 'C', 3, 'F'),
    (NoteSet(frozenset('CDEFGAB')), 'C', -2, 'A'),
    (NoteSet(frozenset('DEFGAbC')), 'A', 1, 'b'),
    (NoteSet(frozenset('DEFGAbC')), 'A', 0, 'A'),
))
def test_add_note_abstract(noteset, note, steps, result):
    assert noteset.add_note(note, steps) == result


def _make_keyboard(notes: Sequence[Note], octaves: Iterable[int] = range(-10, 10)) -> tuple[SpecificNote, ...]:
    return tuple(sorted(SpecificNote(note, octave) for octave, note in itertools.product(octaves, notes)))


def _add_note_specific_generator():
    notesets = [NoteSet(frozenset('CDEFGAB')), NoteSet(frozenset('DEFGAbC'))]
    notesets += list(all_scales['diatonic'].values())
    notesets += [
        Scale.from_name('C', 'h_minor'),
        Scale.from_name('E', 'h_minor'),
        Scale.from_name('d', 'm_minor'),
        Scale.from_name('f', 's_minor'),
        Scale.from_name('b', 'p_minor'),
    ]
    for noteset in notesets:
        noteset_str = f'NoteSet({noteset})'
        if isinstance(noteset, Scale):
            noteset_str = f'Scale({noteset.root.name}, {noteset.name})'
        yield pytest.param(noteset, id=noteset_str)


@pytest.mark.parametrize('noteset', _add_note_specific_generator())
def test_add_note_specific(noteset):
    keyboard = _make_keyboard(noteset.notes_ascending)
    for note, octave, steps in itertools.product(
        [noteset.notes_ascending[0], noteset.notes_ascending[1], noteset.notes_ascending[2], noteset.notes_ascending[-1]],
        [-2, -1, 0, 1, 2],
        [-29, -13, -8, -7, -6, -2, -1, 0, 1, 2, 6, 7, 8, 13, 29],
    ):
        note = SpecificNote(note, octave)
        result = keyboard[keyboard.index(note) + steps]
        assert noteset.add_note(note, steps) == result


@pytest.mark.parametrize('noteset, note, expected', (
    ('CDEFGAB/C', 'A', 'ABdDEfa/A'),
    ('CdeFGab/e', 'D', 'DEfGABC/D'),
    ('Cd/C', 'd', 'dD/d'),
))
def test_transpose(noteset, note, expected):
    assert NoteSet.from_str(noteset).transpose_to(note) is NoteSet.from_str(expected)


@pytest.mark.parametrize('start, stop, noteset, expected', (
    ('C0', 'C1', NoteSet(frozenset(config.chromatic_notes)), 'C0 d0 D0 e0 E0 F0 f0 G0 a0 A0 b0 B0 C1'),
    ('b3', 'E4', NoteSet(frozenset(config.chromatic_notes)), 'b3 B3 C4 d4 D4 e4 E4'),
    ('C0', 'C0', NoteSet(frozenset(config.chromatic_notes)), 'C0'),
    ('C0', 'C1', NoteSet(frozenset('CDEFGAB')), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('C0', 'C1', Scale(frozenset('CDEFGAB'), root='C'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('C0', 'C1', Chord(frozenset('CDEFGAB'), root='C'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('a3', 'f4', NoteSet(frozenset('dEfaB')), 'a3 B3 d4 E4 f4'),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'A0 B0 C1 D1 E1 F1 G1 A1 B1 C2 D2'),
))
def test_note_range(start, stop, noteset, expected):
    assert list(NoteRange(SpecificNote.from_str(start), SpecificNote.from_str(stop), noteset)) == expected.split()


@pytest.mark.parametrize('start, stop, noterange', (
    ('C0', 'C1', NoteRange(SpecificNote('C', 0), SpecificNote('C', 1))),
    ('E1', 'f3', NoteRange(SpecificNote('E', 1), SpecificNote('f', 3))),
    (SpecificNote('E', 1), 'f3', NoteRange(SpecificNote('E', 1), SpecificNote('f', 3))),
    ('E1', SpecificNote('f', 3), NoteRange(SpecificNote('E', 1), SpecificNote('f', 3))),
    (SpecificNote('E', 1), SpecificNote('f', 3), NoteRange(SpecificNote('E', 1), SpecificNote('f', 3))),
))
def test_note_range_from_str(start, stop, noterange):
    assert NoteRange(start, stop) == noterange


def test_noterange_bounds():
    with pytest.raises(ValueError): NoteRange(SpecificNote('D', 2), SpecificNote('C', 1))
    with pytest.raises(KeyError): NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('Cd')))
    with pytest.raises(KeyError): NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('dD')))
    with pytest.raises(KeyError): NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('dDeE')))


def test_noterange_contains():
    assert SpecificNote('D', 1) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 1) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 2) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 3) not in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('D', 1) not in NoteRange(SpecificNote('C', 1), SpecificNote('F', 1), noteset=NoteSet(frozenset('CEF')))


@pytest.mark.parametrize('notes, left, right, distance', (
    ('CDEFGAB', 'E', 'C', 2),
    ('CDEFGAB', 'C', 'E', 5),
    ('CDEFGAB', 'B', 'C', 6),
    ('CDEFGAB', 'C', 'C', 0),
    ('CDEFGAB', 'E', 'A', 4),
    ('CDE', 'D', 'D', 0),
    ('CDE', 'E', 'D', 1),
    ('CDE', 'E', 'C', 2),
    ('CDE', 'C', 'D', 2),
    ('CDE', 'C', 'E', 1),
    ('ab', 'a', 'a', 0),
    ('ab', 'a', 'b', 1),
    ('ab', 'b', 'a', 1),
    ('f', 'f', 'f', 0),
    ('CdDeEFfGaAbB', 'b', 'b', 0),
    ('CdDeEFfGaAbB', 'G', 'C', 7),
    ('CdDeEFfGaAbB', 'C', 'd', 11),
    ('CdDeEFfGaAbB', 'C', 'G', 5),

    ('CDEFGAB', 'E1', 'C1', 2),
    ('CDEFGAB', 'E3', 'C1', 16),
    ('CDEFGAB', 'C1', 'E3', -16),
    ('CDEFGAB', 'C2', 'E-1', 19),
    ('CDEFGAB', 'E-1', 'C2', -19),
    ('CDEFGAB', 'C2', 'E-3', 33),
    ('CDEFGAB', 'E-3', 'C2', -33),
    ('CDEFGAB', 'C-2', 'E-3', 5),
    ('CDEFGAB', 'E-3', 'C-2', -5),
    ('CDEFGAB', 'B1', 'C1', 6),
    ('CDEFGAB', 'C1', 'B1', -6),
    ('CDEFGAB', 'B10', 'C1', 69),
    ('CDEFGAB', 'C1', 'B10', -69),
    ('CDEFGAB', 'C0', 'C0', 0),
    ('CDEFGAB', 'F34', 'F34', 0),
    ('CDEFGAB', 'E4', 'A2', 11),
    ('CDEFGAB', 'A2', 'E4', -11),
    ('CDE', 'D2', 'D2', 0),
    ('CDE', 'D2', 'D3', -3),
    ('CDE', 'E5', 'D4', 4),
    ('CDE', 'D4', 'E5', -4),
    ('CDE', 'E5', 'C4', 5),
    ('CDE', 'C4', 'E5', -5),
    ('ab', 'a3', 'a3', 0),
    ('ab', 'b3', 'a3', 1),
    ('ab', 'a3', 'b3', -1),
    ('ab', 'b4', 'a3', 3),
    ('ab', 'a3', 'b4', -3),
    ('f', 'f0', 'f0', 0),
    ('f', 'f1', 'f0', 1),
    ('f', 'f0', 'f1', -1),
    ('f', 'f2', 'f0', 2),
    ('f', 'f0', 'f2', -2),
    ('f', 'f40', 'f1', 39),
    ('f', 'f1', 'f40', -39),
    ('f', 'f1', 'f-2', 3),
    ('f', 'f-2', 'f1', -3),
    ('f', 'f-4', 'f-7', 3),
    ('f', 'f-7', 'f-4', -3),
    ('CdDeEFfGaAbB', 'b2', 'b2', 0),
    ('CdDeEFfGaAbB', 'G5', 'C3', 31),
    ('CdDeEFfGaAbB', 'C3', 'G5', -31),
    ('CdDeEFfGaAbB', 'C2', 'd-1', 35),
    ('CdDeEFfGaAbB', 'd-1', 'C2', -35),
    ('CdDeEFfGaAbB', 'C-2', 'C-3', 12),
    ('CdDeEFfGaAbB', 'C-3', 'C-2', -12),
    ('CdDeEFfGaAbB', 'C-3', 'C-8', 60),
    ('CdDeEFfGaAbB', 'C-8', 'C-3', -60),
    ('CdDeEFfGaAbB', 'd-3', 'G-8', 54),
    ('CdDeEFfGaAbB', 'G-8', 'd-3', -54),
))
def test_subtract(notes, left, right, distance):
    assert NoteSet(frozenset(notes)).subtract(left, right) == distance


def test_subtract_types():
    noteset = NoteSet(frozenset('CDEFGAB'))
    with pytest.raises(TypeError): noteset.subtract(Note('C'), SpecificNote('D', 1))
    with pytest.raises(TypeError): noteset.subtract(SpecificNote('D', 1), Note('C'))
    with pytest.raises(TypeError): noteset.subtract('C', 'D1')
    with pytest.raises(TypeError): noteset.subtract('D1', 'C')
    with pytest.raises(TypeError): noteset.subtract('C', SpecificNote('D', 1))
    with pytest.raises(TypeError): noteset.subtract('D1', Note('C'))


@pytest.mark.parametrize('start, stop, notes, length', (
    (SpecificNote('C', 1), SpecificNote('G', 1), 'CdDeEFfGaAbB', 8),
    (SpecificNote('D', 1), SpecificNote('G', 3), 'CdDeEFfGaAbB', 30),
    (SpecificNote('D', 1), SpecificNote('D', 1), 'CdDeEFfGaAbB', 1),
    (SpecificNote('E', 1), SpecificNote('b', 1), 'CDEFGAb', 5),
    (SpecificNote('b', 1), SpecificNote('G', 3), 'CDEFGAb', 13),
    (SpecificNote('f', 1), SpecificNote('a', 1), 'fa', 2),
    (SpecificNote('f', 1), SpecificNote('f', 2), 'fa', 3),
    (SpecificNote('f', 1), SpecificNote('a', 3), 'fa', 6),
    (SpecificNote('f', 1), SpecificNote('f', 3), 'f', 3),
))
def test_noterange_len(start, stop, notes, length):
    assert len(NoteRange(start, stop, NoteSet(frozenset(notes)))) == length


def test_noterange_getitem():
    nr = NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert nr[0] == nr[-13] == SpecificNote('C', 1)
    assert nr[1] == nr[-12] == SpecificNote('d', 1)
    assert nr[2] == nr[-11] == SpecificNote('D', 1)
    assert nr[12] == nr[-1] == SpecificNote('C', 2)
    assert nr[11] == nr[-2] == SpecificNote('B', 1)
    assert nr[0:0] == NoteRange(SpecificNote('C', 1), SpecificNote('C', 1))
    assert nr[0:1] == NoteRange(SpecificNote('C', 1), SpecificNote('d', 1))
    assert nr[0:2] == NoteRange(SpecificNote('C', 1), SpecificNote('D', 1))
    assert nr[0:12] == NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    with pytest.raises(IndexError): nr[13]
    with pytest.raises(IndexError): nr[-14]
    with pytest.raises(IndexError): nr[-3: 1]
    with pytest.raises(IndexError): nr[5: 13]

    ns = NoteSet(frozenset('fa'))
    nr = NoteRange(SpecificNote('f', -1), SpecificNote('a', 3), ns)
    assert nr[0] == nr[-10] == SpecificNote('f', -1)
    assert nr[1] == nr[-9] == SpecificNote('a', -1)
    assert nr[2] == nr[-8] == SpecificNote('f', 0)
    assert nr[9] == nr[-1] == SpecificNote('a', 3)
    assert nr[8] == nr[-2] == SpecificNote('f', 3)
    assert nr[0:0] == NoteRange(SpecificNote('f', -1), SpecificNote('f', -1), ns)
    assert nr[0:1] == NoteRange(SpecificNote('f', -1), SpecificNote('a', -1), ns)
    assert nr[0:2] == NoteRange(SpecificNote('f', -1), SpecificNote('f', 0), ns)
    assert nr[0:9] == NoteRange(SpecificNote('f', -1), SpecificNote('a', 3), ns)
    with pytest.raises(IndexError): nr[10]
    with pytest.raises(IndexError): nr[-11]


def test_noterange_list():
    assert list(NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))) == 'C1 d1 D1 e1 E1 F1 f1 G1 a1 A1 b1 B1 C2'.split()
    assert list(NoteRange(SpecificNote('b', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('AbBCdDe')))) == 'b1 B1 C2 d2 D2'.split()

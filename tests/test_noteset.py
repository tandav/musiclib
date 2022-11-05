import itertools
from collections.abc import Sequence

import pytest

from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noteset import NoteSet
from musictool.noteset import bits_to_intervals
from musictool.noteset import intervals_to_bits
from musictool.scale import Scale
from musictool.scale import all_scales


def test_empty():
    NoteSet(frozenset())
    with pytest.raises(KeyError):
        NoteSet(frozenset(), root=Note('C'))


@pytest.mark.parametrize(
    'bits, intervals', (
        ('101011010101', frozenset({0, 2, 4, 5, 7, 9, 11})),
        ('110101101010', frozenset({0, 1, 3, 5, 6, 8, 10})),
        ('101001010100', frozenset({0, 2, 5, 7, 9})),
        ('101101010010', frozenset({0, 2, 3, 5, 7, 10})),
        ('000000000000', frozenset()),
    ),
)
def test_bits_intervals(bits, intervals):
    assert bits_to_intervals(bits) == intervals
    assert intervals_to_bits(intervals) == bits


@pytest.mark.parametrize(
    'string, expected', (
        ('CDEFGAB/C', NoteSet(frozenset(map(Note, 'CDEFGAB')), root=Note('C'))),
        ('CDEFGAB', NoteSet(frozenset(map(Note, 'CDEFGAB')))),
        ('CdeFGab/e', NoteSet(frozenset(map(Note, 'CdeFGab')), root=Note('e'))),
        ('CEG/C', NoteSet(frozenset(map(Note, 'CEG')), root=Note('C'))),
        ('fa/a', NoteSet(frozenset(map(Note, 'fa')), root=Note('a'))),
        ('', NoteSet(frozenset())),
    ),
)
def test_from_str(string, expected):
    assert NoteSet.from_str(string) == expected


@pytest.mark.parametrize(
    'noteset, intervals', (
        (NoteSet.from_str('CDEFGAB/C'), (0, 2, 4, 5, 7, 9, 11)),
        (NoteSet.from_str('DeFGAbC/D'), (0, 1, 3, 5, 7, 8, 10)),
        (NoteSet(frozenset()), ()),
    ),
)
def test_intervals(noteset, intervals):
    assert noteset.intervals_ascending == intervals
    assert noteset.intervals == frozenset(intervals)


@pytest.mark.parametrize(
    'noteset, note_to_interval', [
        (NoteSet.from_str('CDE'), {}),
        (NoteSet.from_str('CDE/C'), {Note('C'): 0, Note('D'): 2, Note('E'): 4}),
    ],
)
def test_note_to_interval(noteset, note_to_interval):
    assert noteset.note_to_interval == note_to_interval


@pytest.mark.parametrize(
    'notes, bits', (
        ('CDEFGAB/C', '101011010101'),
        ('dfb/d', '100001000100'),
        ('', '000000000000'),
    ),
)
def test_bits(notes, bits):
    assert NoteSet.from_str(notes).bits == bits


@pytest.mark.parametrize(
    'value', (
        'CDE',
        set(map(Note, 'CDE')),
        tuple(map(Note, 'CDE')),
        list(map(Note, 'CDE')),
    ),
)
def test_notes_type_is_frozenset(value):
    with pytest.raises(TypeError):
        NoteSet(value)


def test_contains():
    assert Note('C') in NoteSet.from_str('C')
    assert Note('C') not in NoteSet.from_str('D')
    assert NoteSet.from_str('CD') <= NoteSet.from_str('CDE')
    assert NoteSet.from_str('CDE') <= NoteSet.from_str('CDE')
    assert not NoteSet.from_str('CDEF') <= NoteSet.from_str('CDE')
    empty_noteset = NoteSet(frozenset())
    assert Note('C') not in empty_noteset
    assert empty_noteset <= NoteSet.from_str('CDE')


def test_root_validation():
    with pytest.raises(KeyError):
        NoteSet.from_str('AB/E')


def test_note_i():
    fs = frozenset(map(Note, 'CDEfGaB'))
    noteset = NoteSet(fs)
    assert fs == noteset.note_i.keys()
    assert noteset.note_i[Note('C')] == 0
    assert noteset.note_i[Note('B')] == 6
    assert noteset.note_i[Note('f')] == 3
    assert noteset.note_i[Note('G')] == 4
    assert NoteSet(frozenset()).note_i == {}


@pytest.mark.parametrize(
    'intervals, root, expected', (
        (frozenset({0, 4, 7}), 'C', NoteSet.from_str('CEG/C')),
        (frozenset({0, 1, 3, 5, 7, 8, 10}), 'E', NoteSet.from_str('CDEFGAB/E')),
        (frozenset({0, 2, 3, 5, 7, 9, 10}), 'f', NoteSet.from_str('faABdeE/f')),
        (frozenset(), None, NoteSet(frozenset(), root=None)),
    ),
)
def test_from_intervals(intervals, root, expected):
    assert NoteSet.from_intervals(intervals, root) is expected


def test_subclasses_names_unreachable():
    with pytest.raises(KeyError):
        NoteSet.from_name('C', 'major')  # test that Scale names are unreachable
    with pytest.raises(KeyError):
        NoteSet.from_name('e', 'aug')  # test that Chord names are unreachable


@pytest.mark.parametrize(
    'noteset, notes_octave_fit', (
        (NoteSet.from_str('efGd'), 'defG'),
        (NoteSet.from_str('efGd/e'), 'defG'),
        (NoteSet.from_str('FGbBCd/F'), 'CdFGbB'),
        (NoteSet(frozenset()), ''),
    ),
)
def test_notes_octave_fit(noteset, notes_octave_fit):
    assert noteset.notes_octave_fit == tuple(notes_octave_fit)


@pytest.mark.parametrize(
    'noteset, note, steps, result', (
        (NoteSet.from_str('CDEFGAB'), Note('C'), 3, 'F'),
        (NoteSet.from_str('CDEFGAB'), 'C', 3, 'F'),
        (NoteSet.from_str('CDEFGAB'), 'C', -2, 'A'),
        (NoteSet.from_str('DEFGAbC'), 'A', 1, 'b'),
        (NoteSet.from_str('DEFGAbC'), 'A', 0, 'A'),
    ),
)
def test_add_note_abstract(noteset, note, steps, result):
    assert noteset.add_note(note, steps) == result


@pytest.mark.parametrize(
    'noteset, note, steps', (
        (NoteSet(frozenset()), 'A', 1),
        (NoteSet(frozenset()), 'A1', 1),
    ),
)
def test_add_note_empty_noteset(noteset, note, steps):
    with pytest.raises(NotImplementedError):
        noteset.add_note(note, steps)


def _make_keyboard(notes: Sequence[Note], octaves: Sequence[int]) -> tuple[SpecificNote, ...]:
    return tuple(sorted(SpecificNote(note, octave) for octave, note in itertools.product(octaves, notes)))


def _add_note_specific_generator():
    notesets = [NoteSet.from_str('CDEFGAB'), NoteSet.from_str('DEFGAbC')]
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
    keyboard = _make_keyboard(notes=noteset.notes_ascending, octaves=range(-10, 10))
    for note, octave, steps in itertools.product(
        [noteset.notes_ascending[0], noteset.notes_ascending[1], noteset.notes_ascending[2], noteset.notes_ascending[-1]],
        [-2, -1, 0, 1, 2],
        [-29, -13, -8, -7, -6, -2, -1, 0, 1, 2, 6, 7, 8, 13, 29],
    ):
        note = SpecificNote(note, octave)
        result = keyboard[keyboard.index(note) + steps]
        assert noteset.add_note(note, steps) == result


@pytest.mark.parametrize(
    'noteset, root, expected', (
        ('CD/C', 'C', 'CD/C'),
        ('CD/C', 'D', 'CD/D'),
        ('CD/D', 'C', 'CD/C'),
        ('CD', 'C', 'CD/C'),
    ),
)
def test_with_root(noteset, root, expected):
    assert NoteSet.from_str(noteset).with_root(Note(root)) == NoteSet.from_str(expected)


def test_with_root_validation():
    with pytest.raises(NotImplementedError):
        NoteSet(frozenset()).with_root(Note('C'))
    with pytest.raises(KeyError):
        NoteSet.from_str('CD/D').with_root(Note('E'))


@pytest.mark.parametrize(
    'noteset, note, expected', (
        ('CDEFGAB/C', 'A', 'ABdDEfa/A'),
        ('CdeFGab/e', 'D', 'DEfGABC/D'),
        ('Cd/C', 'd', 'dD/d'),
    ),
)
def test_transpose_to(noteset, note, expected):
    assert NoteSet.from_str(noteset).transpose_to(note) is NoteSet.from_str(expected)


@pytest.mark.parametrize(
    'notes, left, right, distance', (
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
    ),
)
def test_subtract(notes, left, right, distance):
    assert NoteSet.from_str(notes).subtract(left, right) == distance


def test_subtract_types():
    noteset = NoteSet.from_str('CDEFGAB')
    with pytest.raises(TypeError):
        noteset.subtract(Note('C'), SpecificNote('D', 1))
    with pytest.raises(TypeError):
        noteset.subtract(SpecificNote('D', 1), Note('C'))
    with pytest.raises(TypeError):
        noteset.subtract('C', 'D1')
    with pytest.raises(TypeError):
        noteset.subtract('D1', 'C')
    with pytest.raises(TypeError):
        noteset.subtract('C', SpecificNote('D', 1))
    with pytest.raises(TypeError):
        noteset.subtract('D1', Note('C'))

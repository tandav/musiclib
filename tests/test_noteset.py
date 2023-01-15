import itertools
from collections.abc import Sequence

import pytest

from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noteset import NoteSet
from musiclib.noteset import bits_to_intervals
from musiclib.noteset import intervals_to_bits
from musiclib.scale import Scale
from musiclib.scale import all_scales


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
    'noteset, bits', (
        (NoteSet.from_str('CDE'), (1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0)),
        (NoteSet.from_str('df'), (0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)),
    ),
)
def test_bits_notes(noteset, bits):
    assert noteset.bits_notes == bits


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
        (NoteSet.from_str('CDEFGAB'), Note('C'), 3, Note('F')),
        (NoteSet.from_str('CDEFGAB'), Note('C'), -2, Note('A')),
        (NoteSet.from_str('DEFGAbC'), Note('A'), 1, Note('b')),
        (NoteSet.from_str('DEFGAbC'), Note('A'), 0, Note('A')),
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
        ('CDEFGAB', Note('E'), Note('C'), 2),
        ('CDEFGAB', Note('C'), Note('E'), 5),
        ('CDEFGAB', Note('B'), Note('C'), 6),
        ('CDEFGAB', Note('C'), Note('C'), 0),
        ('CDEFGAB', Note('E'), Note('A'), 4),
        ('CDE', Note('D'), Note('D'), 0),
        ('CDE', Note('E'), Note('D'), 1),
        ('CDE', Note('E'), Note('C'), 2),
        ('CDE', Note('C'), Note('D'), 2),
        ('CDE', Note('C'), Note('E'), 1),
        ('ab', Note('a'), Note('a'), 0),
        ('ab', Note('a'), Note('b'), 1),
        ('ab', Note('b'), Note('a'), 1),
        ('f', Note('f'), Note('f'), 0),
        ('CdDeEFfGaAbB', Note('b'), Note('b'), 0),
        ('CdDeEFfGaAbB', Note('G'), Note('C'), 7),
        ('CdDeEFfGaAbB', Note('C'), Note('d'), 11),
        ('CdDeEFfGaAbB', Note('C'), Note('G'), 5),

        ('CDEFGAB', SpecificNote('E', 1), SpecificNote('C', 1), 2),
        ('CDEFGAB', SpecificNote('E', 3), SpecificNote('C', 1), 16),
        ('CDEFGAB', SpecificNote('C', 1), SpecificNote('E', 3), -16),
        ('CDEFGAB', SpecificNote('C', 2), SpecificNote('E', -1), 19),
        ('CDEFGAB', SpecificNote('E', -1), SpecificNote('C', 2), -19),
        ('CDEFGAB', SpecificNote('C', 2), SpecificNote('E', -3), 33),
        ('CDEFGAB', SpecificNote('E', -3), SpecificNote('C', 2), -33),
        ('CDEFGAB', SpecificNote('C', -2), SpecificNote('E', -3), 5),
        ('CDEFGAB', SpecificNote('E', -3), SpecificNote('C', -2), -5),
        ('CDEFGAB', SpecificNote('B', 1), SpecificNote('C', 1), 6),
        ('CDEFGAB', SpecificNote('C', 1), SpecificNote('B', 1), -6),
        ('CDEFGAB', SpecificNote('B', 10), SpecificNote('C', 1), 69),
        ('CDEFGAB', SpecificNote('C', 1), SpecificNote('B', 10), -69),
        ('CDEFGAB', SpecificNote('C', 0), SpecificNote('C', 0), 0),
        ('CDEFGAB', SpecificNote('F', 34), SpecificNote('F', 34), 0),
        ('CDEFGAB', SpecificNote('E', 4), SpecificNote('A', 2), 11),
        ('CDEFGAB', SpecificNote('A', 2), SpecificNote('E', 4), -11),
        ('CDE', SpecificNote('D', 2), SpecificNote('D', 2), 0),
        ('CDE', SpecificNote('D', 2), SpecificNote('D', 3), -3),
        ('CDE', SpecificNote('E', 5), SpecificNote('D', 4), 4),
        ('CDE', SpecificNote('D', 4), SpecificNote('E', 5), -4),
        ('CDE', SpecificNote('E', 5), SpecificNote('C', 4), 5),
        ('CDE', SpecificNote('C', 4), SpecificNote('E', 5), -5),
        ('ab', SpecificNote('a', 3), SpecificNote('a', 3), 0),
        ('ab', SpecificNote('b', 3), SpecificNote('a', 3), 1),
        ('ab', SpecificNote('a', 3), SpecificNote('b', 3), -1),
        ('ab', SpecificNote('b', 4), SpecificNote('a', 3), 3),
        ('ab', SpecificNote('a', 3), SpecificNote('b', 4), -3),
        ('f', SpecificNote('f', 0), SpecificNote('f', 0), 0),
        ('f', SpecificNote('f', 1), SpecificNote('f', 0), 1),
        ('f', SpecificNote('f', 0), SpecificNote('f', 1), -1),
        ('f', SpecificNote('f', 2), SpecificNote('f', 0), 2),
        ('f', SpecificNote('f', 0), SpecificNote('f', 2), -2),
        ('f', SpecificNote('f', 40), SpecificNote('f', 1), 39),
        ('f', SpecificNote('f', 1), SpecificNote('f', 40), -39),
        ('f', SpecificNote('f', 1), SpecificNote('f', -2), 3),
        ('f', SpecificNote('f', -2), SpecificNote('f', 1), -3),
        ('f', SpecificNote('f', -4), SpecificNote('f', -7), 3),
        ('f', SpecificNote('f', -7), SpecificNote('f', -4), -3),
        ('CdDeEFfGaAbB', SpecificNote('b', 2), SpecificNote('b', 2), 0),
        ('CdDeEFfGaAbB', SpecificNote('G', 5), SpecificNote('C', 3), 31),
        ('CdDeEFfGaAbB', SpecificNote('C', 3), SpecificNote('G', 5), -31),
        ('CdDeEFfGaAbB', SpecificNote('C', 2), SpecificNote('d', -1), 35),
        ('CdDeEFfGaAbB', SpecificNote('d', -1), SpecificNote('C', 2), -35),
        ('CdDeEFfGaAbB', SpecificNote('C', -2), SpecificNote('C', -3), 12),
        ('CdDeEFfGaAbB', SpecificNote('C', -3), SpecificNote('C', -2), -12),
        ('CdDeEFfGaAbB', SpecificNote('C', -3), SpecificNote('C', -8), 60),
        ('CdDeEFfGaAbB', SpecificNote('C', -8), SpecificNote('C', -3), -60),
        ('CdDeEFfGaAbB', SpecificNote('d', -3), SpecificNote('G', -8), 54),
        ('CdDeEFfGaAbB', SpecificNote('G', -8), SpecificNote('d', -3), -54),
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
        noteset.subtract('C', SpecificNote('D', 1))  # type: ignore
    with pytest.raises(TypeError):
        noteset.subtract('D1', Note('C'))  # type: ignore

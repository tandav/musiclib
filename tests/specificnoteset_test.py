from collections.abc import Sequence
import pytest
from musiclib.note import SpecificNote
from musiclib.noteset import NoteSet
from musiclib import config
from musiclib.noteset import SpecificNoteSet


@pytest.mark.parametrize(
    ('noteset', 'note', 'expected'), [
        (SpecificNoteSet.from_str('C1_E1_G1'), SpecificNote.from_str('A1'), SpecificNoteSet.from_str('A1_d2_E2')),
        (SpecificNoteSet(frozenset()), SpecificNote.from_str('A1'), SpecificNoteSet(frozenset())),
    ],
)
def test_transpose_to_note(noteset, note, expected):
    assert noteset.transpose_to_note(note) == expected


@pytest.mark.parametrize('arg', ['C1_D1_E1', set('C1_D1_E1'), tuple('C1_D1_E1'), list('C1_D1_E1')])
def test_notes_type_is_frozenset(arg):
    with pytest.raises(TypeError):
        SpecificNoteSet(arg)


@pytest.mark.parametrize(
    ('x', 's', 'r'), [
        (SpecificNoteSet.from_str('C1_C2'), "C1_C2", "C1_C2"),
    ],
)
def test_str_repr(x, s, r):
    assert str(x) == s
    assert repr(x) == r


def test_from_str():
    assert SpecificNoteSet.from_str('C1_E1_G1') == SpecificNoteSet(frozenset({SpecificNote('C', 1), SpecificNote('E', 1), SpecificNote('G', 1)}))
    for _ in range(10):
        sns = SpecificNoteSet.random()
        assert SpecificNoteSet.from_str(str(sns)) == sns
    with pytest.raises(ValueError):
        SpecificNoteSet.from_str('C1_C1')
    with pytest.raises(ValueError):
        SpecificNoteSet.from_str('C1_E1_E1')


def test_magic_methods():
    sns = SpecificNoteSet.from_str('C1_E1_G1')
    assert len(sns) == len(sns.notes)
    assert all(sns[i] == sns.notes_ascending[i] for i in range(len(sns)))
    assert tuple(iter(sns)) == sns.notes_ascending
    sns2 = SpecificNoteSet.from_str('d3_f8')
    assert tuple(zip(sns, sns2, strict=False)) == (
        (SpecificNote('C', 1), SpecificNote('d', 3)),
        (SpecificNote('E', 1), SpecificNote('f', 8)),
    )


def test_sub():
    a = SpecificNoteSet.from_str('C1_E1_G1')
    b = SpecificNoteSet.from_str('B0_D1_G1')
    assert a - b == b - a == 3


def test_combinations_order():
    for _ in range(10):
        for n, m in SpecificNoteSet.random().notes_combinations():
            assert n < m


@pytest.mark.parametrize(
    ('specific', 'noteset'), [
        ('C1_E1_G2', NoteSet.from_str('CEG')),
    ],
)
def test_noteset(specific, noteset):
    assert SpecificNoteSet.from_str(specific).noteset == noteset


def test_find_intervals():
    a = SpecificNote('C', 5)
    b = SpecificNote('E', 5)
    c = SpecificNote('G', 5)
    d = SpecificNote('C', 6)
    e = SpecificNote('D', 6)

    assert SpecificNoteSet(frozenset({a, b, c})).find_intervals(7) == ((a, c),)
    assert SpecificNoteSet(frozenset({a, b, c, e})).find_intervals(7) == ((a, c), (c, e))
    assert SpecificNoteSet(frozenset({a, d})).find_intervals(12) == ((a, d),)


@pytest.mark.parametrize(
    ('sns', 'note', 'expected'), [
        ('C3_E3_G3', SpecificNote('C', 0), 'C0_E0_G0'),
        ('F3_A3_C4', SpecificNote('C', 0), 'C0_E0_G0'),
    ],
)
def test_transposed_to_note(sns, note, expected):
    assert SpecificNoteSet.from_str(sns).transpose_to_note(note) == SpecificNoteSet.from_str(expected)


@pytest.mark.parametrize(
    ('sns', 'add', 'expected'), [
        ('C3_E3_G3', -36, 'C0_E0_G0'),
        ('C3_E3_G3', -24, 'C1_E1_G1'),
        ('C3_E3_G3', 0, 'C3_E3_G3'),
        ('C3_E3_G3', 12, 'C4_E4_G4'),
        ('C3_E3_G3', -34, 'D0_f0_A0'),
        ('C3_E3_G3', 13, 'd4_F4_a4'),
    ],
)
def test_add(sns, add, expected):
    assert SpecificNoteSet.from_str(sns) + add == SpecificNoteSet.from_str(expected)
    with pytest.raises(TypeError):
        sns + [1]  # noqa: RUF005


@pytest.mark.parametrize(
    ('start', 'stop', 'noteset', 'expected'), [
        ('C0', 'C1', NoteSet.from_str(config.chromatic_notes), 'C0 d0 D0 e0 E0 F0 f0 G0 a0 A0 b0 B0 C1'),
        ('b3', 'E4', NoteSet.from_str(config.chromatic_notes), 'b3 B3 C4 d4 D4 e4 E4'),
        ('C0', 'C0', NoteSet.from_str(config.chromatic_notes), 'C0'),
        ('C0', 'C1', NoteSet.from_str('CDEFGAB'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
        ('a3', 'f4', NoteSet.from_str('dEfaB'), 'a3 B3 d4 E4 f4'),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'A0 B0 C1 D1 E1 F1 G1 A1 B1 C2 D2'),
    ],
)
def test_from_noterange(start, stop, noteset, expected):
    assert list(SpecificNoteSet.from_noterange(
        SpecificNote.from_str(start), SpecificNote.from_str(stop), noteset)
    ) == [SpecificNote.from_str(s) for s in expected.split()]


def test_from_noterange_bounds():
    with pytest.raises(ValueError):
        SpecificNoteSet.from_noterange(SpecificNote('D', 2), SpecificNote('C', 1))
    with pytest.raises(KeyError):
        SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2), noteset=NoteSet(frozenset()))
    with pytest.raises(KeyError):
        SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet.from_str('Cd'))
    with pytest.raises(KeyError):
        SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet.from_str('dD'))
    with pytest.raises(KeyError):
        SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet.from_str('dDeE'))


def test_from_noterange_contains():
    assert SpecificNote('D', 1) in SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 1) in SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 2) in SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 3) not in SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('D', 1) not in SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('F', 1), noteset=NoteSet.from_str('CEF'))


@pytest.mark.parametrize(
    ('start', 'stop', 'notes', 'length'), [
        (SpecificNote('C', 1), SpecificNote('G', 1), 'CdDeEFfGaAbB', 8),
        (SpecificNote('D', 1), SpecificNote('G', 3), 'CdDeEFfGaAbB', 30),
        (SpecificNote('D', 1), SpecificNote('D', 1), 'CdDeEFfGaAbB', 1),
        (SpecificNote('E', 1), SpecificNote('b', 1), 'CDEFGAb', 5),
        (SpecificNote('b', 1), SpecificNote('G', 3), 'CDEFGAb', 13),
        (SpecificNote('f', 1), SpecificNote('a', 1), 'fa', 2),
        (SpecificNote('f', 1), SpecificNote('f', 2), 'fa', 3),
        (SpecificNote('f', 1), SpecificNote('a', 3), 'fa', 6),
        (SpecificNote('f', 1), SpecificNote('f', 3), 'f', 3),
    ],
)
def test_from_noterange_len(start, stop, notes, length):
    assert len(SpecificNoteSet.from_noterange(start, stop, NoteSet.from_str(notes))) == length


def test_from_noterange_getitem():
    sns = SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert sns[0] == sns[-13] == SpecificNote('C', 1)
    assert sns[1] == sns[-12] == SpecificNote('d', 1)
    assert sns[2] == sns[-11] == SpecificNote('D', 1)
    assert sns[12] == sns[-1] == SpecificNote('C', 2)
    assert sns[11] == sns[-2] == SpecificNote('B', 1)
    # TODO: instabce of sequence[specificnote]
    assert sns[0:0] == SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 1))
    assert sns[0:1] == SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('d', 1))
    assert sns[0:2] == SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('D', 1))
    assert sns[0:12] == SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert sns[1:] == SpecificNoteSet.from_noterange(SpecificNote('d', 1), SpecificNote('C', 2))
    assert sns[:4] == SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('E', 1))
    assert sns[:] == SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2))

    with pytest.raises(IndexError):
        sns[13]
    with pytest.raises(IndexError):
        sns[-14]
    with pytest.raises(IndexError):
        sns[-3: 1]
    with pytest.raises(IndexError):
        sns[5: 13]

    ns = NoteSet.from_str('fa')
    sns = SpecificNoteSet.from_noterange(SpecificNote('f', -1), SpecificNote('a', 3), ns)
    assert sns[0] == sns[-10] == SpecificNote('f', -1)
    assert sns[1] == sns[-9] == SpecificNote('a', -1)
    assert sns[2] == sns[-8] == SpecificNote('f', 0)
    assert sns[9] == sns[-1] == SpecificNote('a', 3)
    assert sns[8] == sns[-2] == SpecificNote('f', 3)
    assert sns[0:0] == SpecificNoteSet.from_noterange(SpecificNote('f', -1), SpecificNote('f', -1), ns)
    assert sns[0:1] == SpecificNoteSet.from_noterange(SpecificNote('f', -1), SpecificNote('a', -1), ns)
    assert sns[0:2] == SpecificNoteSet.from_noterange(SpecificNote('f', -1), SpecificNote('f', 0), ns)
    assert sns[0:9] == SpecificNoteSet.from_noterange(SpecificNote('f', -1), SpecificNote('a', 3), ns)
    with pytest.raises(IndexError):
        sns[10]
    with pytest.raises(IndexError):
        sns[-11]

@pytest.mark.parametrize(
    ('noterange', 'expected'), [
        (SpecificNoteSet.from_noterange(SpecificNote('C', 1), SpecificNote('C', 2)), 'C1 d1 D1 e1 E1 F1 f1 G1 a1 A1 b1 B1 C2'),
        (SpecificNoteSet.from_noterange(SpecificNote('b', 1), SpecificNote('D', 2), noteset=NoteSet.from_str('AbBCdDe')), 'b1 B1 C2 d2 D2'),
    ],
)
def test_from_noterange_list(noterange, expected):
    assert list(noterange) == [SpecificNote.from_str(s) for s in expected.split()]



def test_sequence():
    sns = SpecificNoteSet.random()
    assert isinstance(sns, Sequence)

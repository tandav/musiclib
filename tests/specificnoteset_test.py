import pytest
from musiclib.note import SpecificNote
from musiclib.noteset import NoteSet
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

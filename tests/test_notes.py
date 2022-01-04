import pytest

from musictools.notes import bits_to_intervals
from musictools.notes import intervals_to_bits
from musictools.notes import Notes
from musictools.note import Note
from musictools.note import SpecificNote


@pytest.mark.parametrize('bits, intervals', (
    ('101011010101', frozenset({2, 4, 5, 7, 9, 11})),
    ('110101101010', frozenset({1, 3, 5, 6, 8, 10})),
    ('101001010100', frozenset({2, 5, 7, 9})),
    ('101101010010', frozenset({2, 3, 5, 7, 10})),
))
def test_bits_intervals(bits, intervals):
    assert bits_to_intervals(bits) == intervals
    assert intervals_to_bits(intervals) == bits


@pytest.mark.parametrize('notes, root, bits', (
    (frozenset('CDEFGAB'), 'C', '101011010101'),
    (frozenset('dfb'), 'd', '100001000100'),
))
def test_bits(notes, root, bits):
    assert Notes(notes, root).bits == bits


def test_empty():
    with pytest.raises(ValueError):
        Notes(frozenset())


def test_childs_names_unreachable():
    with pytest.raises(KeyError): # test that Scale names are unreachable
        Notes.from_name('C', 'major')

    with pytest.raises(KeyError): # test that Chord names are unreachable
        Notes.from_name('e', 'aug')


@pytest.mark.parametrize('notes, note, steps, result', (
    ('CDEFGAB', Note('C'), 3, 'F'),
    ('CDEFGAB', 'C', 3, 'F'),
    ('CDEFGAB', 'C', -2, 'A'),
    ('DEFGAbC', 'A', 1, 'b'),
    ('DEFGAbC', 'A', 0, 'A'),
    ('CDEFGAB', SpecificNote('C', 1), 3, SpecificNote('F', 1)),
    ('CDEFGAB', SpecificNote('C', 1), -2, SpecificNote('A', 0)),
    ('CDEFGAB', SpecificNote('G', 5), -22, SpecificNote('F', 2)),
    ('DEFGAbC', SpecificNote('A', 1), 8, SpecificNote('b', 2)),
    ('DEFGAbC', SpecificNote('A', 1), 0, SpecificNote('A', 1)),
    ('DEFGAbC', SpecificNote('A', 2), -7, SpecificNote('A', 1)),
))
def test_add_note(notes, note, steps, result):
    assert Notes(frozenset(notes)).add_note(note, steps) == result

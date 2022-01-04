import pytest

from musictools.notes import bits_to_intervals
from musictools.notes import intervals_to_bits
from musictools.notes import Notes
from musictools.notes import note_range
from musictools.note import Note
from musictools.note import SpecificNote
from musictools.scale import Scale
from musictools.chord import Chord
from musictools.chord import SpecificChord


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


@pytest.mark.parametrize('start, stop, notes, expected', (
    ('C0', 'C1', None, 'C0 d0 D0 e0 E0 F0 f0 G0 a0 A0 b0 B0 C1'),
    ('b3', 'E4', None, 'b3 B3 C4 d4 D4 e4 E4'),
    ('C0', 'C1', Notes(frozenset('CDEFGAB')), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('C0', 'C1', Scale(frozenset('CDEFGAB'), 'C'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('C0', 'C1', Chord(frozenset('CDEFGAB'), 'C'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('a3', 'f4', Notes(frozenset('dEfaB')), 'a3 B3 d4 E4 f4'),
    ('A0', 'D2', Notes(frozenset('CDEFGAB')), 'A0 B0 C1 D1 E1 F1 G1 A1 B1 C2 D2'),
))
def test_note_range(start, stop, notes, expected):
    assert note_range(SpecificNote.from_str(start), SpecificNote.from_str(stop), notes) == tuple(SpecificNote.from_str(s) for s in expected.split())

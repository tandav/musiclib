import pytest

from musictool.chord import Chord
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noteset import NoteRange
from musictool.noteset import NoteSet
from musictool.noteset import bits_to_intervals
from musictool.noteset import intervals_to_bits
from musictool.noteset import note_range
from musictool.scale import Scale


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
    assert NoteSet(notes, root).bits == bits


def test_empty():
    with pytest.raises(ValueError):
        NoteSet(frozenset())


def test_notes_type_is_frozenset():
    with pytest.raises(TypeError):
        NoteSet('CDE')
    with pytest.raises(TypeError):
        NoteSet(set('CDE'))
    with pytest.raises(TypeError):
        NoteSet(tuple('CDE'))
    with pytest.raises(TypeError):
        NoteSet(list('CDE'))


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
    with pytest.raises(KeyError):
        NoteSet(frozenset('AB'), root='E')


def test_note_i():
    fs = frozenset('CDEfGaB')
    noteset = NoteSet(fs)
    assert fs == noteset.note_i.keys()
    assert noteset.note_i['C'] == 0
    assert noteset.note_i['B'] == 6
    assert noteset.note_i['f'] == 3
    assert noteset.note_i['G'] == 4


def test_childs_names_unreachable():
    with pytest.raises(KeyError):  # test that Scale names are unreachable
        NoteSet.from_name('C', 'major')

    with pytest.raises(KeyError):  # test that Chord names are unreachable
        NoteSet.from_name('e', 'aug')


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
    assert NoteSet(frozenset(notes)).add_note(note, steps) == result


@pytest.mark.parametrize('start, stop, noteset, expected', (
    ('C0', 'C1', None, 'C0 d0 D0 e0 E0 F0 f0 G0 a0 A0 b0 B0 C1'),
    ('b3', 'E4', None, 'b3 B3 C4 d4 D4 e4 E4'),
    ('C0', 'C0', None, 'C0'),
    ('C0', 'C1', NoteSet(frozenset('CDEFGAB')), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('C0', 'C1', Scale(frozenset('CDEFGAB'), 'C'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('C0', 'C1', Chord(frozenset('CDEFGAB'), 'C'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
    ('a3', 'f4', NoteSet(frozenset('dEfaB')), 'a3 B3 d4 E4 f4'),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'A0 B0 C1 D1 E1 F1 G1 A1 B1 C2 D2'),
))
def test_note_range(start, stop, noteset, expected):
    assert note_range(SpecificNote.from_str(start), SpecificNote.from_str(stop), noteset) == tuple(SpecificNote.from_str(s) for s in expected.split())


def test_noterange_bounds():
    with pytest.raises(ValueError):
        NoteRange(SpecificNote('D', 2), SpecificNote('C', 1))

    with pytest.raises(KeyError):
        NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('Cd')))
    with pytest.raises(KeyError):
        NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('dD')))
    with pytest.raises(KeyError):
        NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('dDeE')))


def test_noterange_contains():
    assert SpecificNote('D', 1) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 1) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 2) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 3) not in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))


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

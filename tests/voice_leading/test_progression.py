import pytest

from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.noteset import note_range
from musictool.scale import NoteSet
from musictool.scale import Scale
from musictool.voice_leading import progression


def test_list_like():
    p = progression.Progression([0, 1, 2])
    e = [0, 1, 2, 3]
    assert p + [3] == e
    p.append(3)
    assert p == e


@pytest.mark.parametrize('noteset, note_range_, chord_str, transitions, unique_abstract', (
    (Scale.from_name('C', 'major'), ('A0', 'D2'), 'C1_E1_G1', {'B0_E1_G1', 'C1_D1_G1', 'C1_E1_A1', 'C1_E1_F1', 'C1_F1_G1', 'D1_E1_G1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'C1_E1_G1', {'B0_E1_G1', 'C1_D1_G1', 'C1_E1_A1', 'C1_E1_F1', 'C1_F1_G1', 'D1_E1_G1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'C1_D1_E1', {'B0_D1_E1', 'C1_D1_F1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'B0_C1_D1', {'B0_C1_E1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'F1_G1_A1', {'E1_G1_A1', 'F1_G1_B1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'D1_E1_C2', {'C1_E1_C2', 'D1_E1_B1', 'D1_E1_D2', 'D1_F1_C2'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'D1_E1_C2', {'D1_E1_B1', 'D1_F1_C2'}, True),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'C1_E1', {'B0_E1', 'C1_D1', 'C1_F1', 'D1_E1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'C1_D1', {'B0_D1', 'C1_E1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'C1_D1_E1_F1', {'B0_D1_E1_F1', 'C1_D1_E1_G1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'C1_D1_E1_F1', {'B0_D1_E1_F1', 'C1_D1_E1_G1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'C1_E1_G1_B1', {'B0_E1_G1_B1', 'D1_E1_G1_B1', 'C1_E1_F1_B1', 'C1_E1_A1_B1', 'C1_E1_G1_C2', 'C1_F1_G1_B1', 'C1_D1_G1_B1', 'C1_E1_G1_A1'}, False),
    (NoteSet(frozenset('CDEFGAB')), ('A0', 'D2'), 'C1_E1_G1_B1', {'D1_E1_G1_B1', 'C1_D1_G1_B1', 'C1_E1_F1_B1', 'C1_E1_A1_B1', 'C1_E1_G1_A1', 'C1_F1_G1_B1'}, True),
    (NoteSet(frozenset('CdeFGab')), ('a0', 'd2'), 'C1_e1_G1', {'b0_e1_G1', 'C1_d1_G1', 'C1_e1_a1', 'C1_e1_F1', 'C1_F1_G1', 'd1_e1_G1'}, False),
))
def test_chord_transitons(noteset, note_range_, chord_str, transitions, unique_abstract):
    chord = SpecificChord.from_str(chord_str)
    note_range_ = note_range(SpecificNote.from_str(note_range_[0]), SpecificNote.from_str(note_range_[1]), noteset)
    assert set(map(str, progression.chord_transitons(chord, note_range_, unique_abstract))) == transitions


def test_transition_graph():
    note_range_ = note_range(SpecificNote('A', 0), SpecificNote('D', 2), NoteSet(frozenset('CDEFGAB')))
    graph = progression.transition_graph(SpecificChord.from_str('C1_E1_G1'), note_range_)
    assert len(graph) == 80
    assert sum(map(len, graph.values())) == 300


def test_transpose_uniqiue_key():
    a = SpecificChord.random()
    b = SpecificChord.random()
    c = SpecificChord.random()
    d = SpecificChord.random()

    d_ = SpecificChord(frozenset((d.notes_ascending[0] + 12,) + d.notes_ascending[1:]))

    p0 = a, b, c, d
    p1 = a, b, c, d_
    p2 = tuple(SpecificChord(frozenset(n + 12 for n in chord.notes)) for chord in p0)
    p3 = tuple(SpecificChord(frozenset(n + 1 for n in chord.notes)) for chord in p0)

    assert progression.transpose_uniqiue_key(p0) != progression.transpose_uniqiue_key(p1)
    assert progression.transpose_uniqiue_key(p0) == progression.transpose_uniqiue_key(p2)
    assert progression.transpose_uniqiue_key(p0) != progression.transpose_uniqiue_key(p3)

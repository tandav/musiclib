import textwrap

import pytest

from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.noteset import NoteRange
from musictool.noteset import NoteSet
from musictool.scale import Scale
from musictool.voice_leading import transition


@pytest.mark.parametrize('a, b, expected', (
    (
        'C3_E3_G3_C4',
        'B2_E3_G3_C4',
        """\
        C3_E3_G3_C4
        /  |  |  |
        B2_E3_G3_C4""",
    ),
))
def test_transition(a, b, expected):
    assert repr(transition.Transition(SpecificChord.from_str(a), SpecificChord.from_str(b))) == textwrap.dedent(expected)


@pytest.mark.parametrize('start, stop, noteset, chord_str, transitions, unique_abstract', (
    ('A0', 'D2', Scale.from_name('C', 'major'), 'C1_E1_G1', {'B0_E1_G1', 'C1_D1_G1', 'C1_E1_A1', 'C1_E1_F1', 'C1_F1_G1', 'D1_E1_G1'}, False),
    ('A0', 'D2', Scale.from_name('E', 'phrygian'), 'C1_E1_G1', {'B0_E1_G1', 'C1_D1_G1', 'C1_E1_A1', 'C1_E1_F1', 'C1_F1_G1', 'D1_E1_G1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'C1_E1_G1', {'B0_E1_G1', 'C1_D1_G1', 'C1_E1_A1', 'C1_E1_F1', 'C1_F1_G1', 'D1_E1_G1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'C1_D1_E1', {'B0_D1_E1', 'C1_D1_F1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'B0_C1_D1', {'A0_C1_D1', 'B0_C1_E1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'B1_C2_D2', {'A1_C2_D2'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'A1_B1_C2', {'G1_B1_C2', 'A1_B1_D2'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'F1_G1_A1', {'E1_G1_A1', 'F1_G1_B1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'D1_E1_C2', {'C1_E1_C2', 'D1_E1_B1', 'D1_E1_D2', 'D1_F1_C2'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'D1_E1_C2', {'D1_E1_B1', 'D1_F1_C2'}, True),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'C1_E1', {'B0_E1', 'C1_D1', 'C1_F1', 'D1_E1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'C1_D1', {'B0_D1', 'C1_E1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'C1_D1_E1_F1', {'B0_D1_E1_F1', 'C1_D1_E1_G1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'C1_D1_E1_F1', {'B0_D1_E1_F1', 'C1_D1_E1_G1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'C1_E1_G1_B1', {'B0_E1_G1_B1', 'D1_E1_G1_B1', 'C1_E1_F1_B1', 'C1_E1_A1_B1', 'C1_E1_G1_C2', 'C1_F1_G1_B1', 'C1_D1_G1_B1', 'C1_E1_G1_A1'}, False),
    ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'C1_E1_G1_B1', {'D1_E1_G1_B1', 'C1_D1_G1_B1', 'C1_E1_F1_B1', 'C1_E1_A1_B1', 'C1_E1_G1_A1', 'C1_F1_G1_B1'}, True),
    ('a0', 'd2', NoteSet(frozenset('CdeFGab')), 'C1_e1_G1', {'b0_e1_G1', 'C1_d1_G1', 'C1_e1_a1', 'C1_e1_F1', 'C1_F1_G1', 'd1_e1_G1'}, False),
))
def test_chord_transitions(start, stop, noteset, chord_str, transitions, unique_abstract):
    chord = SpecificChord.from_str(chord_str)
    noterange = NoteRange(start, stop, noteset)
    assert set(map(str, transition.chord_transitions(chord, noterange, unique_abstract))) == transitions


@pytest.mark.parametrize('noteset', (
    NoteSet(frozenset('CDEFGAB')),
    Scale.from_name('C', 'major'),
    Scale.from_name('E', 'phrygian'),
))
def test_transition_graph(noteset):
    noterange = NoteRange(SpecificNote('A', 0), SpecificNote('D', 2), noteset)
    graph = transition.transition_graph(SpecificChord.from_str('C1_E1_G1'), noterange)
    assert len(graph) == 165
    assert sum(map(len, graph.values())) == 720

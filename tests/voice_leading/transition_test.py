import itertools
import textwrap

import pytest
from musiclib.noteset import SpecificNoteSet
from musiclib.note import SpecificNote
from musiclib.noterange import NoteRange
from musiclib.noteset import NoteSet
from musiclib.scale import Scale
from musiclib.voice_leading import transition


@pytest.mark.parametrize(
    ('a', 'b', 'expected'), [
        (
            'C3_E3_G3_C4',
            'B2_E3_G3_C4',
            """\
        C3_E3_G3_C4
        /  |  |  |
        B2_E3_G3_C4""",
        ),
    ],
)
def test_transition(a, b, expected):
    assert repr(transition.Transition(SpecificNoteSet.from_str(a), SpecificNoteSet.from_str(b))) == textwrap.dedent(expected)


@pytest.mark.parametrize(
    ('start', 'stop', 'noteset', 'chord_str', 'transitions', 'unique_abstract', 'same_length'), [
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_E1_G1', {'B0_E1_G1', 'C1_D1_G1', 'C1_E1_A1', 'C1_E1_F1', 'C1_F1_G1', 'D1_E1_G1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_D1_E1', {'B0_D1_E1', 'C1_D1_F1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'B0_C1_D1', {'A0_C1_D1', 'B0_C1_E1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'B1_C2_D2', {'A1_C2_D2'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'A1_B1_C2', {'G1_B1_C2', 'A1_B1_D2'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'F1_G1_A1', {'E1_G1_A1', 'F1_G1_B1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'D1_E1_C2', {'C1_E1_C2', 'D1_E1_B1', 'D1_E1_D2', 'D1_F1_C2'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'D1_E1_C2', {'D1_E1_B1', 'D1_F1_C2'}, True, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_E1', {'B0_E1', 'C1_D1', 'C1_F1', 'D1_E1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_D1', {'B0_D1', 'C1_E1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_D1', {'B0_D1', 'C1_E1', 'C1', 'D1'}, False, False),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_D1_E1_F1', {'B0_D1_E1_F1', 'C1_D1_E1_G1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_D1_E1_F1', {'B0_D1_E1_F1', 'C1_D1_E1_G1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_E1_G1_B1', {'B0_E1_G1_B1', 'D1_E1_G1_B1', 'C1_E1_F1_B1', 'C1_E1_A1_B1', 'C1_E1_G1_C2', 'C1_F1_G1_B1', 'C1_D1_G1_B1', 'C1_E1_G1_A1'}, False, True),
        ('A0', 'D2', NoteSet.from_str('CDEFGAB'), 'C1_E1_G1_B1', {'D1_E1_G1_B1', 'C1_D1_G1_B1', 'C1_E1_F1_B1', 'C1_E1_A1_B1', 'C1_E1_G1_A1', 'C1_F1_G1_B1'}, True, True),
        ('a0', 'd2', NoteSet.from_str('CdeFGab'), 'C1_e1_G1', {'b0_e1_G1', 'C1_d1_G1', 'C1_e1_a1', 'C1_e1_F1', 'C1_F1_G1', 'd1_e1_G1'}, False, True),
    ],
)
def test_chord_transitions(start, stop, noteset, chord_str, transitions, unique_abstract, same_length):
    chord = SpecificNoteSet.from_str(chord_str)
    noterange = NoteRange(start, stop, noteset)
    assert set(map(str, transition.chord_transitions(chord, noterange, unique_abstract=unique_abstract, same_length=same_length))) == transitions


@pytest.mark.parametrize(
    'noteset', [
        NoteSet.from_str('CDEFGAB'),
        Scale.from_name('C', 'major').noteset,
        Scale.from_name('E', 'phrygian').noteset,
    ],
)
def test_transition_graph(noteset):
    noterange = NoteRange(SpecificNote('A', 0), SpecificNote('D', 2), noteset)
    graph = transition.transition_graph(SpecificNoteSet.from_str('C1_E1_G1'), noterange)
    assert len(graph) == 165
    assert sum(map(len, graph.values())) == 720


def test_transition_graph_same_length():
    noteset = Scale.from_name('C', 'major').noteset
    noterange = NoteRange(SpecificNote('A', 0), SpecificNote('D', 2), noteset)
    graph = transition.transition_graph(SpecificNoteSet.from_str('C1_E1_G1'), noterange, same_length=False)
    abstract_graph = transition.abstract_graph(graph)
    assert len(graph) == 231

    s = {
        NoteSet(frozenset(comb))
        for n in range(1, 4)
        for comb in itertools.combinations(noteset.notes, n)
    }
    assert s == abstract_graph.keys()


@pytest.mark.parametrize(
    ('graph', 'expected'), [
        (
            {SpecificNoteSet.from_str('F1_G1'): frozenset(map(SpecificNoteSet.from_str, ('E1_G1', 'F1', 'F1_A1', 'G1')))},
            {NoteSet.from_str('FG'): frozenset(map(NoteSet.from_str, 'EG F G FA'.split()))},
        ),
    ],
)
def test_abstract_graph(graph, expected):
    assert transition.abstract_graph(graph) == expected

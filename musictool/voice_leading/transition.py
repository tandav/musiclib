from collections import defaultdict

from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.noterange import NoteRange
from musictool.noteset import NoteSet

SpecificChordGraph = dict[SpecificChord, frozenset[SpecificChord]]
AbstractChordGraph = dict[NoteSet, frozenset[NoteSet]]


class Transition:
    def __init__(self, a: SpecificChord, b: SpecificChord):
        self.a = a
        self.b = b

    @staticmethod
    def arrow(a: SpecificNote, b: SpecificNote) -> str:
        if a < b: return '︎\\'
        elif a == b: return '|'
        else: return '/'

    def __repr__(self):
        return '\n'.join((
            str(self.a),
            '  '.join(self.arrow(na, nb) for na, nb in zip(self.a, self.b, strict=True)),
            str(self.b),
        ))


def chord_transitions(
    chord: SpecificChord,
    noterange: NoteRange,
    unique_abstract: bool = False,
    same_length: bool = True,
) -> frozenset[SpecificChord]:
    out = set()
    for note in chord:
        for add in (-1, 1):
            if (new_note := noterange.noteset.add_note(note, add)) not in noterange:
                continue
            notes = chord.notes - {note} | {new_note}
            if same_length and len(notes) != len(chord.notes):
                continue
            if unique_abstract and len(notes) > len({n.abstract for n in notes}):
                continue
            out.add(SpecificChord(notes))
    return frozenset(out)


def transition_graph(
    start_chord: SpecificChord,
    noterange: NoteRange,
    unique_abstract: bool = False,
    same_length: bool = True,
) -> dict[SpecificChord, frozenset[SpecificChord]]:
    graph: defaultdict[SpecificChord, set[SpecificChord]] = defaultdict(set)

    def _graph(chord: SpecificChord) -> None:
        if chord in graph:
            return
        childs = chord_transitions(chord, noterange, unique_abstract, same_length)
        graph[chord] |= childs
        for child in childs:
            _graph(child)

    _graph(start_chord)
    return {k: frozenset(v) for k, v in graph.items()}


def abstract_graph(g: SpecificChordGraph) -> AbstractChordGraph:
    graph: defaultdict[NoteSet, set[NoteSet]] = defaultdict(set)

    for k, v in g.items():
        graph[k.abstract] |= {c.abstract for c in v}

    return {k: frozenset(v) for k, v in graph.items()}

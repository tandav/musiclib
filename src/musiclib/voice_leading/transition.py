from collections import defaultdict

from musiclib.noteset import NoteSet
from musiclib.noteset import SpecificNoteSet

SpecificChordGraph = dict[SpecificNoteSet, frozenset[SpecificNoteSet]]
AbstractChordGraph = dict[NoteSet, frozenset[NoteSet]]


def chord_transitions(
    chord: SpecificNoteSet,
    space: SpecificNoteSet,
    *,
    unique_abstract: bool = False,
    same_length: bool = True,
) -> frozenset[SpecificNoteSet]:
    out = set()
    for note in chord:
        for add in (-1, 1):
            if (new_note := space.noteset.add_note(note, add)) not in space:
                continue
            notes = chord.notes - {note} | {new_note}
            if same_length and len(notes) != len(chord.notes):
                continue
            if unique_abstract and len(notes) > len({n.abstract for n in notes}):
                continue
            out.add(SpecificNoteSet(notes))
    return frozenset(out)


def transition_graph(
    start_chord: SpecificNoteSet,
    space: SpecificNoteSet,
    *,
    unique_abstract: bool = False,
    same_length: bool = True,
) -> dict[SpecificNoteSet, frozenset[SpecificNoteSet]]:
    graph: defaultdict[SpecificNoteSet, set[SpecificNoteSet]] = defaultdict(set)

    def _graph(chord: SpecificNoteSet) -> None:
        if chord in graph:
            return
        childs = chord_transitions(
            chord,
            space,
            unique_abstract=unique_abstract,
            same_length=same_length,
        )
        graph[chord] |= childs
        for child in childs:
            _graph(child)

    _graph(start_chord)
    return {k: frozenset(v) for k, v in graph.items()}


def abstract_graph(g: SpecificChordGraph) -> AbstractChordGraph:
    graph: defaultdict[NoteSet, set[NoteSet]] = defaultdict(set)

    for k, v in g.items():
        graph[k.noteset] |= {c.noteset for c in v}

    return {k: frozenset(v) for k, v in graph.items()}

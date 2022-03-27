
from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.noteset import NoteRange


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
) -> frozenset[SpecificChord]:
    out = set()
    for note in chord:
        for add in (-1, 1):
            if (new_note := noterange.noteset.add_note(note, add)) not in noterange:
                continue
            notes = chord.notes - {note} | {new_note}
            if len(notes) != len(chord.notes):
                continue
            if unique_abstract and len(notes) > len({n.abstract for n in notes}):
                continue
            out.add(SpecificChord(notes))
    return frozenset(out)


def transition_graph(start_chord: SpecificChord, noterange: NoteRange) -> dict[SpecificChord, frozenset[SpecificChord]]:
    graph: dict[SpecificChord, frozenset[SpecificChord]] = {}

    def _graph(chord: SpecificChord) -> None:
        if chord in graph:
            return
        childs = chord_transitions(chord, noterange)
        graph[chord] = childs
        for child in childs:
            _graph(child)

    _graph(start_chord)
    return graph

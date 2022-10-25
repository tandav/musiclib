from musictool.chord import Chord
from musictool.scale import Scale


def str_to_chord_progression(s: Scale, progression: str) -> tuple[Chord, ...]:
    return tuple(s.triads[s.notes_ascending.index(c)] for c in progression)

import itertools

import pipe as P

from . import config
from .chord import Chord
from .chord import SpecificChord
from .chord import name_to_intervals
from .note import SpecificNote


def all_triads(octave_limit=(4, 6)):
    all_notes = tuple(
        SpecificNote(note, octave)
        for octave, note in itertools.product(
            range(octave_limit[0], octave_limit[1] + 1),
            config.chromatic_notes
        )
    )
    n3 = tuple(itertools.combinations(all_notes, 3))  # all 3-notes subsets
    all_chords = frozenset(
        Chord.from_name(root, name)
        for root, name in itertools.product(config.chromatic_notes, name_to_intervals)
    )

    rootless_2_rootfull = {chord.rootless: chord for chord in all_chords}

    return (
        n3
        | P.Map(frozenset)
        | P.Map(SpecificChord)
        | P.ValueBy(lambda chord: rootless_2_rootfull.get(chord.abstract))
        | P.FilterValues()
        | P.Append(lambda x: f'{x[1].root.name} {x[1].name}')
        | P.Pipe(tuple)
    )

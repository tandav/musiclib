import functools
import itertools

import pipe21 as P

from . import config
from .chord import Chord
from .chord import SpecificChord
from .chord import name_to_intervals
from .note import SpecificNote
from .scale import Scale


def all_triads(octaves=(4, 5, 6)):
    all_notes = tuple(
        SpecificNote(note, octave)
        for octave, note in itertools.product(octaves, config.chromatic_notes)
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


@functools.cache
def have_parallel_interval(a: SpecificChord, b: SpecificChord, interval: int) -> bool:
    '''
    parallel in same voices!
    if there'are eg fifth in 1st and fifth in 2nd chord but not from same voices
    - then it allowed (aint considered parallel) (test it)

    a1 - b1
    a0 - b0
    todo: what about fifths + octave (eg C5 G6 -> F5 C6)
    '''
    voice_transitions = tuple(zip(a.notes_ascending, b.notes_ascending))
    for (a0, b0), (a1, b1) in itertools.combinations(voice_transitions, 2):
        if abs(a0 - a1) % 12 == interval == abs(b0 - b1) % 12:
            return True


@functools.cache
def have_hidden_parallel(a: SpecificChord, b: SpecificChord, interval: int) -> bool:
    """
    hidden/direct parallel/consecutive interval is when:
        1. outer voices (lower and higher) go in same direction (instead of oblique or contrary motion)
        2. they approach param:interval
    voice leading rules often forbid hidden fifths and octaves (param:interval = 7, 0) (explanation: 12 % 12 == 0 octave equal to unison)
    """
    a_low, a_high = a.notes_ascending[0], a.notes_ascending[-1]
    b_low, b_high = b.notes_ascending[0], b.notes_ascending[-1]

    is_same_direction = (a_low < b_low and a_high < b_high) or (a_low > b_low and a_high > b_high)
    if is_same_direction and (b_high - b_low) % 12 == interval:
        return True
    return False


@functools.cache
def have_voice_overlap(a: SpecificChord, b: SpecificChord) -> bool:
    n = len(b.notes_ascending)
    for i in range(n):
        upper = i < n - 1 and b.notes_ascending[i] > a.notes_ascending[i + 1]
        lower = i > 0 and b.notes_ascending[i] < a.notes_ascending[i - 1]
        if upper or lower:
            return True
    return False


@functools.cache
def have_large_leaps(a: SpecificChord, b: SpecificChord, interval: int) -> bool:
    return any(
        abs(an - bn) > interval
        for an, bn in zip(a.notes_ascending, b.notes_ascending)
    )


@functools.cache
def iter_inversions(chord: Chord, octaves):
    notes_iterators = []
    for note in chord.notes:
        notes_iterators.append([SpecificNote(note, octave) for octave in octaves])
    return itertools.product(*notes_iterators) | P.Map(lambda notes: SpecificChord(frozenset(notes), root=chord.root)) | P.Pipe(tuple)


def iter_inversions_chord_progression(progression, octaves):
    inversions = []
    for chord in progression:
        inversions.append(iter_inversions(chord, octaves))
    yield from itertools.product(*inversions)


def progression_dist(p):
    n = len(p)
    return sum(abs(p[i] - p[(i + 1) % n]) for i in range(n))


def progression_key(progression):
    '''invariant to transposition'''
    return tuple(chord.intervals for chord in progression)


@functools.cache
def check_all_transitions_not(p, f, *args):
    n = len(p)
    return all(not f(p[i], p[(i + 1) % n], *args) for i in range(n))


def no_double_leading_tone(p, s: Scale):
    '''leading tone here is 7th and 2nd not of a scale, maybe'''
    return all


@functools.cache
def notes_are_chord(notes: tuple, scale_chords: frozenset[Chord]):
    abstract = tuple(n.abstract for n in notes)
    abstract_fz = frozenset(abstract)

    for chord in scale_chords:
        if abstract_fz == chord.notes:
            root = chord.root
            break
    else:
        return
    chord = SpecificChord(frozenset(notes), root)
    if chord.notes_ascending[0].abstract != root:
        return
    yield chord


def unique_roots(progression):
    return len(progression) == len(frozenset(chord.root for chord in progression))


def make_progressions(
    scale: Scale,
    note_range: tuple[SpecificNote],
):
    return (
        note_range
        | P.Filter(lambda note: note.abstract in set(scale.notes))
        | P.Pipe(lambda it: itertools.combinations(it, 4))  # 4 voice chords
        | P.FlatMap(lambda notes: notes_are_chord(notes, frozenset(chord for chord in scale.chords if chord.name != 'diminished')))
        | P.Pipe(lambda it: itertools.permutations(it, 4))
        | P.Filter(lambda p: p[0].root.name == 'C')
        | P.Filter(unique_roots)
        | P.Filter(lambda p: check_all_transitions_not(p, have_parallel_interval, 0))
        | P.Filter(lambda p: check_all_transitions_not(p, have_parallel_interval, 7))
        | P.Filter(lambda p: check_all_transitions_not(p, have_hidden_parallel, 0))
        | P.Filter(lambda p: check_all_transitions_not(p, have_hidden_parallel, 7))
        | P.Filter(lambda p: check_all_transitions_not(p, have_voice_overlap))
        | P.Filter(lambda p: check_all_transitions_not(p, have_large_leaps, 5))
        | P.Pipe(tuple)
    )

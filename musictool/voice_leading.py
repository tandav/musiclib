import collections
import functools
import itertools
import operator
import random
from collections.abc import Iterable

import pipe21 as P

from musictool import config
from musictool.chord import Chord
from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.scale import Scale
from musictool.scale import parallel
from musictool.scale import relative
from musictool.util.iteration import iter_cycles
from musictool.util.iteration import unique


def all_triads(octaves=(4, 5, 6)):
    all_notes = tuple(
        SpecificNote(note, octave)
        for octave, note in itertools.product(octaves, config.chromatic_notes)
    )
    n3 = tuple(itertools.combinations(all_notes, 3))  # all 3-notes subsets
    all_chords = frozenset(
        Chord.from_name(root, name)
        for root, name in itertools.product(config.chromatic_notes, Chord.name_to_intervals)
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
    return False


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
def no_large_spacing(c: SpecificChord, max_interval=12):
    return all(c.notes_ascending[i] - c.notes_ascending[i - 1] <= max_interval for i in range(1, len(c.notes_ascending)))


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


def possible_chords(scale: Scale, note_range: tuple[SpecificNote]) -> tuple[SpecificChord]:
    return (
        note_range
        | P.Filter(lambda note: note.abstract in set(scale.notes))
        | P.Pipe(lambda it: itertools.combinations(it, 4))  # 4 voice chords
        | P.FlatMap(lambda notes: notes_are_chord(notes, frozenset(chord for chord in scale.triads if chord.name != 'diminished')))
        | P.Filter(no_large_spacing)
        | P.Pipe(tuple)
    )


def c_not_c(chords: Iterable[SpecificChord]) -> tuple[list[SpecificChord], list[SpecificChord]]:
    c_chords, not_c_chords = [], []
    for c in chords:
        if c.root.name == 'C':
            c_chords.append(c)
        else:
            not_c_chords.append(c)
    return c_chords, not_c_chords


checks = (
    lambda a, b: have_parallel_interval(a, b, 0),
    lambda a, b: have_parallel_interval(a, b, 7),
    lambda a, b: have_hidden_parallel(a, b, 0),
    lambda a, b: have_hidden_parallel(a, b, 7),
    lambda a, b: have_voice_overlap(a, b),
    lambda a, b: have_large_leaps(a, b, 5),
)


@functools.cache
def no_bad_checks(a: SpecificChord, b: SpecificChord):
    return all(not check(a, b) for check in checks)


def transpose_uniqiue_key(progression):
    origin = progression[0].notes_ascending[0]

    return (
        origin.abstract.i,
        tuple(frozenset(note - origin for note in chord.notes) for chord in progression)
    )


def make_progressions(
    scale: Scale,
    note_range: tuple[SpecificNote],
    n=4,
):
    return (
        iter_cycles(
            n,
            options=possible_chords(scale, note_range),
            curr_prev_constraint=no_bad_checks,
            i_constraints={0: lambda chord: chord.root == scale.root},
            unique_key=lambda chord: chord.root,
        )
        | P.Pipe(lambda it: unique(it, key=transpose_uniqiue_key))
        | P.KeyBy(progression_dist)
        | P.Pipe(lambda x: sorted(x, key=operator.itemgetter(0)))
        | P.Pipe(tuple)
    )


@functools.cache
def all_chords(chord: Chord, note_range, n_notes: int = 3):
    chord_notes = tuple(n for n in note_range if n.abstract in chord.notes)
    return (
        itertools.combinations(chord_notes, n_notes)
        | P.Filter(lambda notes: frozenset(n.abstract for n in notes) == chord.notes)
        | P.Map(lambda notes: SpecificChord(notes, root=chord.root))
        | P.Filter(no_large_spacing)
        | P.Pipe(tuple)
    )


def make_progressions_v2(
    abstract_progression: tuple[Chord],
    n_notes: int = 3,
):
    chord_2_all_chords = tuple(all_chords(chord, config.note_range, n_notes) for chord in abstract_progression)
    return (
        iter_cycles(
            n=len(abstract_progression),
            options=chord_2_all_chords,
            options_separated=True,
            curr_prev_constraint=no_bad_checks,
        )
        | P.Pipe(lambda it: unique(it, key=transpose_uniqiue_key))
        | P.KeyBy(progression_dist)
        | P.Pipe(lambda x: sorted(x, key=operator.itemgetter(0)))
        | P.Pipe(tuple)
    )


def random_progression(s: Scale, n: int = 8, parallel_prob=0.2):
    assert s.kind == 'diatonic'
    parallel_ = parallel(s)
    relative_ = relative(s)
    print('scale', 'parallel', 'relative')
    print(s, parallel_, relative_)
    print('=' * 100)
    chords = []
    chords.append(s.triads[0])

    steps = {'major': (0, 1, 2, 3, 4, 5), 'minor': (0, 2, 3, 4, 5, 6)}[s.name]  # disable diminished

    for _ in range(n - 1):
        step = random.choice(steps)
        s_ = s if random.random() > parallel_prob else parallel_
        c = s_.triads[step]
        print(s_, c)
        chords.append(c)
    return chords


def str_to_chord_progression(s: Scale, progression: str):
    return tuple(s.triads[s.notes.index(c)] for c in progression)


def chord_transitons(
    chord: SpecificChord,
    note_range: tuple[SpecificNote],
    unique_abstract: bool = True,
) -> frozenset[SpecificChord]:
    out = set()
    note_to_i = {note: i for i, note in enumerate(note_range)}

    for note in chord.notes_ascending:
        for add in (-1, 1):
            i = note_to_i[note] + add
            if i == 0 or i == len(note_range):
                continue
            notes = chord.notes - {note} | {note_range[i]}
            if len(notes) != 3:
                continue
            if unique_abstract and len(notes) > len({n.abstract for n in notes}):
                continue
            out.add(SpecificChord(notes))
    return frozenset(out)


def transition_graph(start_chord: SpecificChord, note_range: tuple[SpecificNote]) -> dict[SpecificChord, frozenset[SpecificChord]]:
    graph = collections.defaultdict(set)

    def _graph(chord: SpecificChord):
        if chord in graph:
            return
        childs = chord_transitons(chord, note_range)
        for child in childs:
            graph[chord].add(child)
        for child in childs:
            _graph(child)

    _graph(start_chord)
    graph = dict(graph)
    return graph

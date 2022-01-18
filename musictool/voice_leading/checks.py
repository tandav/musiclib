import functools
import itertools

from musictool.chord import SpecificChord
from musictool.scale import Scale


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


def make_major_scale_leading_tone_resolving_semitone_up(
    a: SpecificChord,
    b: SpecificChord,
    s: Scale,
) -> bool:
    if s.name != 'major':
        raise ValueError('not ero')
    leading_tone = [note for note in a.notes if note.abstract == s.notes_ascending[-1]][0]
    tonic = [note for note in b.notes if note.abstract == s.root][0]
    return tonic - leading_tone == 1

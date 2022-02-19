import functools
import itertools
from collections.abc import Callable

from musictool.chord import SpecificChord
from musictool.progression import Progression
from musictool.scale import Scale


def chord_check_cache(f: Callable):
    cache = {}
    cache_info = {'hits': 0, 'misses': 0, 'currsize': 0}

    @functools.wraps(f)
    def inner(a: SpecificChord, b: SpecificChord, *args) -> bool:
        a, b = Progression((a, b)).transposed_to_C0
        key = a, b, *args
        cached = cache.get(key)
        if cached is not None:
            cache_info['hits'] += 1
            return cached
        cache_info['misses'] += 1
        cache_info['currsize'] += 1
        computed = f(a, b, *args)
        cache[key] = computed
        return computed
    inner._cache = cache
    inner._cache_info = cache_info
    return inner


@chord_check_cache
def parallel_interval(a: SpecificChord, b: SpecificChord, interval: int, /) -> bool:
    '''
    parallel in same voices!
    if there'are eg fifth in 1st and fifth in 2nd chord but not from same voices
    - then it allowed (aint considered parallel) (test it)

    a1 - b1
    a0 - b0
    todo: what about fifths + octave (eg C5 G6 -> F5 C6)
    '''
    voice_transitions = tuple(zip(a, b))
    for (a0, b0), (a1, b1) in itertools.combinations(voice_transitions, 2):
        if abs(a0 - a1) % 12 == interval == abs(b0 - b1) % 12:
            return True
    return False


@chord_check_cache
def hidden_parallel(a: SpecificChord, b: SpecificChord, interval: int, /) -> bool:
    """
    hidden/direct parallel/consecutive interval is when:
        1. outer voices (lower and higher) go in same direction (instead of oblique or contrary motion)
        2. they approach param:interval
    voice leading rules often forbid hidden fifths and octaves (param:interval = 7, 0) (explanation: 12 % 12 == 0 octave equal to unison)
    """
    a_low, a_high = a[0], a[-1]
    b_low, b_high = b[0], b[-1]

    is_same_direction = (a_low < b_low and a_high < b_high) or (a_low > b_low and a_high > b_high)
    return is_same_direction and (b_high - b_low) % 12 == interval


@chord_check_cache
def voice_crossing(a: SpecificChord, b: SpecificChord, /) -> bool:
    n = len(b)
    for i in range(n):
        upper = i < n - 1 and b[i] > a[i + 1]
        lower = i > 0 and b[i] < a[i - 1]
        if upper or lower:
            return True
    return False


@chord_check_cache
def large_leaps(a: SpecificChord, b: SpecificChord, interval: int, /) -> bool:
    return any(abs(an - bn) > interval for an, bn in zip(a, b))


def large_spacing(c: SpecificChord, max_interval=12, /):
    return any(b - a > max_interval for a, b in itertools.pairwise(c))


def small_spacing(c: SpecificChord, min_interval=3, /):
    return any(b - a < min_interval for a, b in itertools.pairwise(c))


@chord_check_cache
def make_major_scale_leading_tone_resolving_semitone_up(
    a: SpecificChord,
    b: SpecificChord,
    s: Scale,
    /,
) -> bool:
    if s.name != 'major':
        raise ValueError('not ero')
    leading_tone = [note for note in a.notes if note.abstract == s.notes_ascending[-1]][0]
    tonic = [note for note in b.notes if note.abstract == s.root][0]
    return tonic - leading_tone == 1

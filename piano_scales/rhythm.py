import itertools
import random
import statistics
from collections import deque

import pipe21 as P

from . import util

beats_per_minute = 120  #
beats_per_second = beats_per_minute / 60
beats_per_bar = 4  #
bar_seconds = beats_per_bar / beats_per_second
bar_notes = 16  # kinda grid size
note_seconds = bar_seconds / bar_notes


def random_rhythm(n_notes: int | None = None):
    if not (0 < n_notes <= bar_notes):
        raise ValueError(f'number of notes should be more than 1 and less than bar_notes={bar_notes}')
    if n_notes is None:
        n_notes = random.randint(1, bar_notes)
    r = [1] * n_notes + [0] * (bar_notes - n_notes)
    random.shuffle(r)
    return tuple(r)


def has_contiguous_ones(x):
    return (
        x[0] == 1 and x[-1] == 1
        or any(len(list(g)) > 1 for k, g in itertools.groupby(x, key=bool) if k)
    )


def no_contiguous_ones(prev, curr):
    return not (prev == curr == 1)


def score(x):
    """spacings variance"""
    # rotate until first element == 1, TODO: optimize rotation
    x = deque(x)
    while x[0] != 1:
        x.rotate(-1)

    spacings = [len(list(g)) for k, g in itertools.groupby(x, key=bool) if not k]
    if len(spacings) == 1:  # TODO: try normalize into 0..1
        return float('inf')
    return statistics.variance(spacings)


def make_rhythms(n_notes: int | None = None):
    rhythms = util.iter_cycles(
        n=bar_notes,
        options=(0, 1),
        curr_prev_constraint=no_contiguous_ones,
    )

    if n_notes is not None:
        rhythms = rhythms | P.Filter(lambda r: sum(r) == n_notes)

    return (
        rhythms
        | P.KeyBy(score)
        | P.Pipe(sorted)
        | P.Pipe(tuple)
    )

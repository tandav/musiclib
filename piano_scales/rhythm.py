import itertools
import random
import statistics
from collections import deque
from typing import Optional

beats_per_minute = 120  #
beats_per_second = beats_per_minute / 60
beats_per_bar = 4  #
bar_seconds = beats_per_bar / beats_per_second
bar_notes = 16  # kinda grid size
note_seconds = bar_seconds / bar_notes


def random_rhythm(n_notes: Optional[int] = None):
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

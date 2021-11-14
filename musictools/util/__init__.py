import itertools
import random
import string
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Optional

from musictools import config

# @functools.lru_cache(1024)
# def sort_notes(notes: Iterable):
#     return ''.join(sorted(notes, key=config.chromatic_notes.find))


def hex_to_rgb(color):
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgba_to_rgb(rgb_background, rgba_color):
    '''https://stackoverflow.com/a/21576659/4204843'''

    alpha = rgba_color[3]

    return (
        int((1 - alpha) * rgb_background[0] + alpha * rgba_color[0]),
        int((1 - alpha) * rgb_background[1] + alpha * rgba_color[1]),
        int((1 - alpha) * rgb_background[2] + alpha * rgba_color[2]),
    )


def iter_scales(kind, start=None):
    scales = getattr(config, kind)
    it = itertools.cycle(scales)
    if start:
        it = itertools.dropwhile(lambda x: x != start, it)
    it = itertools.islice(it, len(scales))
    return list(it)


n_intersect_notes_to_n_shared_chords = {7: 7, 6: 4, 5: 2, 4: 0, 3: 0, 2: 0}


def cprint(*args, color=None, **kwargs):
    colormap = dict(
        BLACK='30m',
        RED='31m',
        GREEN='32m',
        YELLOW='33m',
        BLUE='34m',
        MAGENTA='35m',
        CYAN='36m',
        WHITE='37m',
        UNDERLINE='4m',
    )
    if color is None:
        print(*args, **kwargs)
    else:
        print('\033[' + colormap[color], end='')
        print(*args, **kwargs)
        print('\033[0m', end='')


def unique(iterable, key=lambda x: x):
    seen = set()
    for item in iterable:
        ki = key(item)
        if ki in seen:
            continue
        seen.add(ki)
        yield item


def iter_cycles(
    n: int,
    options: Iterable,
    curr_prev_constraint: Optional[Callable] = None,
    first_constraint: Optional[Callable] = None,
    unique_key=None,
    prefix: Optional[Sequence] = None,
) -> Sequence:
    cycle = list(prefix) if prefix else list()
    if len(cycle) == 0:
        first_options = filter(first_constraint, options) if first_constraint else options
        for op in first_options:
            yield from iter_cycles(n, options, curr_prev_constraint, first_constraint, unique_key, prefix=[op])
    else:
        if unique_key:
            # options = frozenset(options) - frozenset(prefix)
            prefix_keys = frozenset(unique_key(op) for op in prefix)
            options = frozenset(op for op in options if unique_key(op) not in prefix_keys)
        for op in options:
            if curr_prev_constraint is not None and not curr_prev_constraint(cycle[-1], op):
                continue
            candidate = cycle + [op]
            if len(candidate) == n:
                if curr_prev_constraint is not None and not curr_prev_constraint(candidate[-1], candidate[0]):
                    continue
                yield tuple(candidate)
            else:
                yield from iter_cycles(n, options, curr_prev_constraint, first_constraint, unique_key, prefix=candidate)


def minmax_scaler(value, oldmin, oldmax, newmin=0.0, newmax=1.0):
    '''
    >>> minmax_scaler(50, 0, 100, 0.0, 1.0)
    0.5
    '''
    return (value - oldmin) * (newmax - newmin) / (oldmax - oldmin) + newmin


def rel_to_abs_w(value): return int(minmax_scaler(value, 0, 1, 0, config.frame_width))
def rel_to_abs_h(value): return int(minmax_scaler(value, 0, 1, 0, config.frame_height))


def rel_to_abs(x, y):
    """xy: coordinates in fractions of screen"""
    return rel_to_abs_w(x), rel_to_abs_h(y)


def random_xy():
    return random.randrange(config.frame_width), random.randrange(config.frame_height)


def random_text(words=tuple(''.join(random.choices(string.ascii_letters, k=random.randint(1, 15))) for _ in range(200))):
    return random.choice(words)


def random_rgb():
    return random.randrange(255), random.randrange(255), random.randrange(255)


def random_rgba():
    return random.randrange(255), random.randrange(255), random.randrange(255), 255


def ago(e):
    # e: pass timedelta between timestamps in 1579812524 format
    e *= 1000  # convert to 1579812524000 format
    t = round(e / 1000)
    n = round(t / 60)
    r = round(n / 60)
    o = round(r / 24)
    i = round(o / 30)
    a = round(i / 12)
    if e < 0: return 'just now'
    elif t < 10: return 'just now'
    elif t < 45: return str(t) + ' seconds ago'
    elif t < 90: return 'a minute ago'
    elif n < 45: return str(n) + ' minutes ago'
    elif n < 90: return 'an hour ago'
    elif r < 24: return str(r) + ' hours ago'
    elif r < 36: return 'a day ago'
    elif o < 30: return str(o) + ' days ago'
    elif o < 45: return 'a month ago'
    elif i < 12: return str(i) + ' months ago'
    elif i < 18: return 'a year ago'
    else: return str(a) + ' years ago'

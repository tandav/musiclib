import itertools
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence

from . import config

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
    curr_prev_constraint: Callable | None = None,
    first_constraint: Callable | None = None,
    unique_key=None,
    prefix: Sequence | None = None,
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

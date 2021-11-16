import itertools
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Optional

from musictools import config


def iter_scales(kind, start=None):
    scales = getattr(config, kind)
    it = itertools.cycle(scales)
    if start:
        it = itertools.dropwhile(lambda x: x != start, it)
    it = itertools.islice(it, len(scales))
    return list(it)


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

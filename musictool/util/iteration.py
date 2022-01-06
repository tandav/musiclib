import itertools
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence

from musictool import config


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
    options: Iterable | Sequence[Iterable],
    options_separated: bool = False,
    curr_prev_constraint: Callable | None = None,
    i_constraints: dict[int, Callable] = dict(),
    # first_constraint: Callable | None = None,
    unique_key=None,
    prefix: Sequence = tuple(),
) -> Sequence:
    cycle = list(prefix) if prefix else list()

    if options_separated:
        ops = options[len(cycle)]
    else:
        ops = options

    if i_constraint := i_constraints.get(len(cycle)):
        ops = filter(i_constraint, ops)

    if unique_key:
        # options = frozenset(options) - frozenset(prefix)
        prefix_keys = frozenset(unique_key(op) for op in prefix)
        ops = frozenset(op for op in ops if unique_key(op) not in prefix_keys)

    for op in ops:
        if len(cycle) > 0 and curr_prev_constraint is not None and not curr_prev_constraint(cycle[-1], op):
            continue
        candidate = cycle + [op]
        if len(candidate) == n:
            if curr_prev_constraint is not None and not curr_prev_constraint(candidate[-1], candidate[0]):
                continue
            yield tuple(candidate)
        else:
            yield from iter_cycles(n, options, options_separated, curr_prev_constraint, i_constraints, unique_key, prefix=candidate)

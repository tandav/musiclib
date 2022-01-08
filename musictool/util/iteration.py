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


def sequence_builder(
    n: int,
    options: Iterable | Sequence[Iterable],
    options_separated: bool = False,
    curr_prev_constraint: Callable | None = None,
    candidate_constraint: Callable | None = None,
    i_constraints: dict[int, Callable] = dict(),
    unique_key: Callable | None = None,
    loop: bool = True,
    prefix: Sequence = tuple(),
) -> Sequence:
    """build a sequence of elements from options
    Parameters
    ----------
    n : int
        len of returned sequence
    options: Iterable
        on each build step use one of the `options`
    options_separated : bool
        if True options should be a Sequence of separate options for each step
    curr_prev_constraint
    candidate_constraint
    i_constraints
    unique_key: Callable | None
        if not None, sequence elements should have unique keys
    loop : bool
        if True then also checks curr_prev_constraint(seq[-1], seq[0])
    prefix:

    Returns
    -------
    Sequence
    """
    seq = list(prefix) if prefix else list()

    ops = options[len(seq)] if options_separated else options

    if i_constraint := i_constraints.get(len(seq)):
        ops = filter(i_constraint, ops)

    if unique_key:
        prefix_keys = frozenset(unique_key(op) for op in prefix)
        ops = frozenset(op for op in ops if unique_key(op) not in prefix_keys)

    if len(seq) > 0 and curr_prev_constraint is not None:
        ops = (op for op in ops if curr_prev_constraint(seq[-1], op))

    for op in ops:
        candidate = seq + [op]
        if candidate_constraint is not None and not candidate_constraint(candidate):
            continue
        if len(candidate) == n:
            if curr_prev_constraint is not None and loop and not curr_prev_constraint(candidate[-1], candidate[0]):
                continue
            yield tuple(candidate)
        else:
            yield from sequence_builder(n, options, options_separated, curr_prev_constraint, candidate_constraint, i_constraints, unique_key, loop, prefix=candidate)

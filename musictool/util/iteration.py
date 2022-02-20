import itertools
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Literal

import tqdm

from musictool import config


def iter_scales(kind, start=None):
    scales = getattr(config, kind)
    it = itertools.cycle(scales)
    if start:
        it = itertools.dropwhile(lambda x: x != start, it)
    it = itertools.islice(it, len(scales))
    return list(it)


# @functools.cache ?
def sequence_builder(
    n: int,
    options: Iterable | Sequence[Iterable] | Callable,
    options_kind: Literal['iterable', 'fixed_per_step', 'callable_from_curr'] = 'iterable',
    curr_prev_constraint: dict[int, Callable] | None = None,
    candidate_constraint: Callable | None = None,
    i_constraints: dict[int, Callable] = dict(),
    unique_key: Callable | None = None,
    loop: bool = False,
    prefix: Sequence = tuple(),
) -> Sequence:
    """build a sequence of elements from options
    Parameters
    ----------
    n : int
        len of returned sequence
    options: Iterable
        on each build step use one of the `options`
    options_kind : str
        'iterable: - todo
        'fixed_per_step: - todo
        'callable_from_curr: - todo
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
    if options_kind == 'iterable':
        options_seq = tuple(options)
        options = frozenset(options_seq)
        if len(options_seq) != len(options):
            raise ValueError('options should be unique')
        ops = options
    elif options_kind == 'fixed_per_step':
        ops = options[len(seq)]
    elif options_kind == 'callable_from_curr':
        assert prefix
        ops = options(seq[-1])
    else:
        raise ValueError('unsupported options_kind')

    if i_constraint := i_constraints.get(len(seq)):
        ops = filter(i_constraint, ops)

    if unique_key:
        prefix_keys = frozenset(unique_key(op) for op in prefix)
        ops = frozenset(op for op in ops if unique_key(op) not in prefix_keys)

    if curr_prev_constraint is not None:

        if abs(max(curr_prev_constraint.keys())) >= n:
            raise IndexError('max index to look back in curr_prev_constraint should be less than n')

        for k, f in curr_prev_constraint.items():
            if abs(k) > len(seq):
                continue
            ops = [op for op in ops if f(seq[k], op)]

    if not prefix:
        ops = tqdm.tqdm(ops)

    for op in ops:
        candidate = seq + [op]
        if candidate_constraint is not None and not candidate_constraint(candidate):
            continue
        if len(candidate) == n:
            if curr_prev_constraint is not None and loop:
                for k, f in curr_prev_constraint.items():
                    if any(not f(candidate[(i + k) % n], candidate[i]) for i in range(abs(k))):
                        break
                else:
                    yield tuple(candidate)
            else:
                yield tuple(candidate)
        else:
            yield from sequence_builder(n, options, options_kind, curr_prev_constraint, candidate_constraint, i_constraints, unique_key, loop, prefix=candidate)

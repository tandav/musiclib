from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any
from typing import TypeVar

import tqdm

Op = TypeVar('Op')

OpsIterable = Iterable[Op]
OpsFixedPerStep = Sequence[Iterable[Op]]
OpsCallableFromCurr = Callable[[Op], Iterable[Op]]


OPTIONS_EXCEPTION = TypeError('options, options_i, options_callable are mutually exclusive. Only 1 must be not None')


class SequenceBuilder:
    def __init__(
        self,
        n: int,
        options: OpsIterable[Op] | None = None,
        options_i: OpsFixedPerStep[Op] | None = None,
        options_callable: OpsCallableFromCurr[Op] | None = None,
        curr_prev_constraint: dict[int, Callable[[Op, Op], bool]] | None = None,
        candidate_constraint: Callable[[tuple[Op, ...]], bool] | None = None,
        i_constraints: dict[int, Callable[[Op], bool]] | None = None,
        unique_key: Callable[[Op], Any] | None = None,
        loop: bool = False,
        prefix: tuple[Op, ...] = (),
    ):
        self.n = n
        self.options: frozenset[Op] | None
        self.options_i: OpsFixedPerStep[Op] | None
        self.options_callable: OpsCallableFromCurr[Op] | None

        if options is not None:
            if not (options_i is None and options_callable is None):
                raise OPTIONS_EXCEPTION
            options_seq = tuple(options)
            options_fset = frozenset(options_seq)
            if len(options_seq) != len(options_fset):
                raise ValueError('options should be unique')
            self.options = options_fset
            self.generate_options = self._generate_options_iterable
        elif options_i is not None:
            if not (options is None and options_callable is None):
                raise OPTIONS_EXCEPTION
            self.options = options
            self.generate_options = self._generate_options_fixed_per_step
        elif options_callable is not None:
            if not (options is None and options_i is None):
                raise OPTIONS_EXCEPTION
            self.options = options
            self.generate_options = self._generate_options_callable_from_curr
        self.options_i = options_i
        self.options_callable = options_callable

        if curr_prev_constraint is not None and not all(k < 0 for k in curr_prev_constraint.keys()):
            raise KeyError('curr_prev_constraint keys must be negative')
        self.curr_prev_constraint = curr_prev_constraint
        self.candidate_constraint = candidate_constraint
        self.i_constraints = i_constraints
        self.unique_key = unique_key
        self.loop = loop
        self.prefix = prefix

    def _generate_options_iterable(self, seq: Sequence[Op]) -> Iterable[Op]:
        if self.options is not None:
            return self.options
        raise TypeError

    def _generate_options_fixed_per_step(self, seq: Sequence[Op]) -> Iterable[Op]:
        if self.options_i is not None:
            return self.options_i[len(seq)]
        raise TypeError

    def _generate_options_callable_from_curr(self, seq: Sequence[Op]) -> Iterable[Op]:
        if self.options_callable is not None:
            return self.options_callable(seq[-1])
        raise TypeError

    def __iter__(self):
        return self._iter(self.prefix)

    def _iter(self, prefix: tuple[Op, ...] = ()) -> Iterable[tuple[Op, ...]]:
        seq = prefix or ()
        ops = self.generate_options(seq)
        if self.i_constraints is not None and (i_constraint := self.i_constraints.get(len(seq))):
            ops = filter(i_constraint, ops)

        if self.unique_key:
            prefix_keys = frozenset(self.unique_key(op) for op in prefix)
            ops = frozenset(op for op in ops if self.unique_key(op) not in prefix_keys)

        if self.curr_prev_constraint:

            if abs(max(self.curr_prev_constraint.keys())) >= self.n:
                raise IndexError('max index to look back in curr_prev_constraint should be less than n')

            for k, f in self.curr_prev_constraint.items():
                if abs(k) > len(seq):
                    continue
                ops = [op for op in ops if f(seq[k], op)]

        if not prefix:
            ops = tqdm.tqdm(ops)

        for op in ops:
            candidate = seq + (op,)
            if self.candidate_constraint is not None and not self.candidate_constraint(candidate):
                continue
            if len(candidate) == self.n:
                if self.curr_prev_constraint and self.loop:
                    for k, f in self.curr_prev_constraint.items():
                        if any(not f(candidate[(i + k) % self.n], candidate[i]) for i in range(abs(k))):
                            break
                    else:
                        yield tuple(candidate)
                else:
                    yield tuple(candidate)
            else:
                yield from self._iter(prefix=candidate)

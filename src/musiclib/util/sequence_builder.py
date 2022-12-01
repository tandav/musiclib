from __future__ import annotations

import itertools
import pickle
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Any
from typing import TypeVar

import tqdm

Op = TypeVar('Op')

OpsIterable = Iterable[Op]
OpsFixedPerStep = Sequence[Iterable[Op]]
OpsCallableFromCurr = Callable[[Op], Iterable[Op]]


OPTIONS_EXCEPTION = TypeError('options, options_i, options_callable are mutually exclusive. Only 1 must be not None')


class SequenceBuilder:
    def __init__(  # noqa: C901
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
        parallel: bool = False,
    ):
        if parallel:
            try:
                pickle.dumps(options)
                pickle.dumps(options_i)
                pickle.dumps(options_callable)
                pickle.dumps(curr_prev_constraint)
                pickle.dumps(candidate_constraint)
                pickle.dumps(i_constraints)
                pickle.dumps(unique_key)
            except BaseException:
                raise pickle.PickleError('parallel=True requires all arguments should be picklable')

        self.n = n
        self.options: tuple[Op, ...] | None
        self.options_i: OpsFixedPerStep[Op] | None
        self.options_callable: OpsCallableFromCurr[Op] | None

        if options is not None:
            if not (options_i is None and options_callable is None):
                raise OPTIONS_EXCEPTION
            options_seq = tuple(options)
            if len(options_seq) != len(frozenset(options_seq)):
                raise ValueError('options should be unique')
            self.options = options_seq
            self.generate_options = self._generate_options_iterable
        elif options_i is not None:
            if not (options is None and options_callable is None):
                raise OPTIONS_EXCEPTION
            if len(options_i) != n:
                raise ValueError('options_i should have options for each step up to n')
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
        self.parallel = parallel

    def _generate_options_iterable(self, seq: tuple[Op, ...]) -> Iterable[Op]:
        if self.options is not None:
            return self.options
        raise TypeError

    def _generate_options_fixed_per_step(self, seq: tuple[Op, ...]) -> Iterable[Op]:
        if self.options_i is not None:
            return self.options_i[len(seq)]
        raise TypeError

    def _generate_options_callable_from_curr(self, seq: tuple[Op, ...]) -> Iterable[Op]:
        if self.options_callable is not None:
            return self.options_callable(seq[-1])
        raise TypeError

    def __iter__(self) -> Generator[tuple[Op, ...], None, None]:
        return self._iter(self.prefix)

    def _iter(self, prefix: tuple[Op, ...] = ()) -> Generator[tuple[Op, ...], None, None]:
        seq = prefix or ()
        ops = self.generate_options(seq)

        if self.i_constraints is not None and (i_constraint := self.i_constraints.get(len(seq))):
            ops = filter(i_constraint, ops)

        if self.unique_key:
            prefix_keys = frozenset(self.unique_key(op) for op in prefix)
            ops = [op for op in ops if self.unique_key(op) not in prefix_keys]

        if self.curr_prev_constraint:

            if abs(max(self.curr_prev_constraint.keys())) >= self.n:
                raise IndexError('max index to look back in curr_prev_constraint should be less than n')

            for k, f in self.curr_prev_constraint.items():
                if abs(k) > len(seq):
                    continue
                ops = [op for op in ops if f(seq[k], op)]
        ops = tuple(ops)
        map_func = partial(self._generate_candidates, seq=seq)

        if len(prefix) == len(self.prefix):
            if self.parallel:
                with ProcessPoolExecutor() as executor:
                    for it in tqdm.tqdm(executor.map(map_func, ops), total=len(ops)):
                        yield from it
                return
            else:
                it = tqdm.tqdm(map(map_func, ops), total=len(ops))
        else:
            it = map(map_func, ops)
        it = itertools.chain.from_iterable(it)
        yield from it

    def _generate_candidates(self, op: Op, seq: tuple[Op, ...]) -> Iterable[tuple[Op, ...]]:
        def inner() -> Iterable[tuple[Op, ...]]:
            candidate = seq + (op,)
            if self.candidate_constraint is not None and not self.candidate_constraint(candidate):
                return
            if len(candidate) < self.n:
                yield from self._iter(prefix=candidate)
                return
            if self.curr_prev_constraint and self.loop and not all(
                f(candidate[(i + k) % self.n], candidate[i])
                for k, f in self.curr_prev_constraint.items()
                    for i in range(abs(k))
            ):
                return
            yield candidate
        out = tuple(inner())
        return out

from __future__ import annotations

import itertools
import pickle
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import TypeVar
from functools import partial
import tqdm
from types import LambdaType

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
            except:
                raise pickle.PickleError('parallel=True requires all arguments should be picklable')
            # if options_callable is not None and isinstance(options_callable, LambdaType):
            #     raise pickle.PickleError('all functions parameters should not be lambdas (parallel requires picklable callables)')
            # if candidate_constraint is not None and isinstance(candidate_constraint, LambdaType):
            #     raise pickle.PickleError('all functions parameters should not be lambdas (parallel requires picklable callables)')
            # if isinstance(unique_key, LambdaType):
            #     raise pickle.PickleError('all functions parameters should not be lambdas (parallel requires picklable callables)')
            # if curr_prev_constraint is not None and any(isinstance(f, LambdaType) for f in curr_prev_constraint.values()):
            #     raise pickle.PickleError('all functions parameters should not be lambdas (parallel requires picklable callables)')
            # if i_constraints is not None and any(isinstance(f, LambdaType) for f in i_constraints.values()):
            #     raise pickle.PickleError('all functions parameters should not be lambdas (parallel requires picklable callables)')
        # if (parallel and (
        #     (options_callable is not None and isinstance(options_callable, LambdaType)) or
        #     (candidate_constraint is not None and isinstance(candidate_constraint, LambdaType)) or
        #     (isinstance(unique_key, LambdaType)) or
        #     (curr_prev_constraint is not None and any(isinstance(f, LambdaType) for f in curr_prev_constraint.values())) or
        #     (i_constraints is not None and any(isinstance(f, LambdaType) for f in i_constraints.values()))
        # )):
        #     raise pickle.PickleError('all functions parameters should not be lambdas (parallel requires picklable callables)')

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
        self.parallel = parallel

        pickle.dumps(self.__iter__)
        pickle.dumps(self._generate_candidates)

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

        def _chain_helper(op):
            return self._generate_candidates(op, seq)
        # def _chain_helper(op):
        #     return tuple(self._generate_candidates(op, seq))
        # def _chain_helper(op, self, seq):
        #     return self._generate_candidates(op, seq)

        # print(pickle.dumps(_chain_helper))

        if len(prefix) == len(self.prefix):
            ops = tqdm.tqdm(ops)

            if self.parallel:
                # with ThreadPoolExecutor() as executor:
                with ProcessPoolExecutor() as executor:
                    # it = executor.map(_chain_helper, ops)
                    # it = executor.map(partial(_chain_helper, self=self, seq=seq), ops)
                    # TODO: minimal example in separate file with ProcessPoolExecutor and generator
                    it = executor.map(partial(self._generate_candidates, seq=seq), ops)
            else:
                it = map(_chain_helper, ops)
            it = itertools.chain.from_iterable(it)
            yield from it
        else:
            it = map(_chain_helper, ops)
            it = itertools.chain.from_iterable(it)
            yield from it

    # def _generate_candidates(self, op: Op, seq: tuple[Op, ...]) -> Iterable[tuple[Op, ...]]:
    #     candidate = seq + (op,)
    #     if self.candidate_constraint is not None and not self.candidate_constraint(candidate):
    #         return
    #     if len(candidate) == self.n:
    #         if self.curr_prev_constraint and self.loop:
    #             for k, f in self.curr_prev_constraint.items():
    #                 if any(not f(candidate[(i + k) % self.n], candidate[i]) for i in range(abs(k))):
    #                     break
    #             else:
    #                 yield tuple(candidate)
    #         else:
    #             yield tuple(candidate)
    #     else:
    #         yield from self._iter(prefix=candidate)

    def _generate_candidates(self, op: Op, seq: tuple[Op, ...]) -> Iterable[tuple[Op, ...]]:
        def inner():
            candidate = seq + (op,)
            if self.candidate_constraint is not None and not self.candidate_constraint(candidate):
                return
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
        return tuple(inner())

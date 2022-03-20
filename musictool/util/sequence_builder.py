import itertools
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any
from typing import Literal
from typing import Type
from typing import TypeGuard
from typing import TypeVar
import tqdm

Op = TypeVar('Op')

OpsIterable = Iterable[Op]
OpsFixedPerStep = Sequence[Iterable[Op]]
OpsCallableFromCurr = Callable[[Op], Iterable[Op]]


class SequenceBuilder:
    def __init__(
        self,
        n: int,
        options: OpsIterable | OpsFixedPerStep | OpsCallableFromCurr,
        options_type: type = OpsIterable,
        # options_type: Literal['iterable', 'fixed_per_step', 'callable_from_curr'] = 'iterable',
        curr_prev_constraint: dict[int, Callable[[Op, Op], bool]] | None = None,
        candidate_constraint: Callable[[tuple[Op, ...]], bool] | None = None,
        i_constraints: dict[int, Callable[[tuple[Op, ...]], bool]] = dict(),
        unique_key: Callable[[Op], Any] | None = None,
        loop: bool = False,
        prefix: tuple[Op, ...] = tuple(),
    ):
        self.n = n
        self.options = options
        self.options_type = options_type
        self.curr_prev_constraint = curr_prev_constraint
        self.candidate_constraint = candidate_constraint
        self.i_constraints = i_constraints
        self.unique_key = unique_key
        self.loop = loop
        self.prefix = prefix

    @classmethod
    def ops_iterable(
        cls,
        n: int,
        options: OpsIterable,
        curr_prev_constraint: dict[int, Callable[[Op, Op], bool]] | None = None,
        candidate_constraint: Callable[[tuple[Op, ...]], bool] | None = None,
        i_constraints: dict[int, Callable[[tuple[Op, ...]], bool]] = dict(),
        unique_key: Callable[[Op], Any] | None = None,
        loop: bool = False,
        prefix: tuple[Op, ...] = tuple(),
    ):
        options_seq = tuple(options)
        options = frozenset(options_seq)
        if len(options_seq) != len(options):
            raise ValueError('options should be unique')
        return cls(n, options, OpsIterable, curr_prev_constraint, candidate_constraint, i_constraints, unique_key, loop, prefix)

    @classmethod
    def ops_fixed_per_step(
        cls,
        n: int,
        options: OpsFixedPerStep,
        curr_prev_constraint: dict[int, Callable[[Op, Op], bool]] | None = None,
        candidate_constraint: Callable[[tuple[Op, ...]], bool] | None = None,
        i_constraints: dict[int, Callable[[tuple[Op, ...]], bool]] = dict(),
        unique_key: Callable[[Op], Any] | None = None,
        loop: bool = False,
        prefix: tuple[Op, ...] = tuple(),
    ):
        return cls(n, options, OpsFixedPerStep, curr_prev_constraint, candidate_constraint, i_constraints, unique_key, loop, prefix)

    @classmethod
    def ops_callable_from_curr(
        cls,
        n: int,
        options: OpsCallableFromCurr,
        curr_prev_constraint: dict[int, Callable[[Op, Op], bool]] | None = None,
        candidate_constraint: Callable[[tuple[Op, ...]], bool] | None = None,
        i_constraints: dict[int, Callable[[tuple[Op, ...]], bool]] = dict(),
        unique_key: Callable[[Op], Any] | None = None,
        loop: bool = False,
        prefix: tuple[Op, ...] = tuple(),
    ):
        return cls(n, options, OpsCallableFromCurr, curr_prev_constraint, candidate_constraint, i_constraints, unique_key, loop, prefix)

    def generate_options(self, seq: Sequence[Op]):
        if self.options_type is OpsIterable:
            return self.options
        elif self.options_type is OpsFixedPerStep:
            return self.options[len(seq)]
        elif self.options_type is OpsCallableFromCurr:
            return self.options(seq[-1])

    # def __next__(self): ...
    def __iter__(self):
        return self._iter(self.prefix)

    def _iter(self,
        prefix: tuple[Op, ...] = tuple(),
    ):
        seq = prefix or tuple()
        ops = self.generate_options(seq)
        if i_constraint := self.i_constraints.get(len(seq)):
            ops = filter(i_constraint, ops)

        if self.unique_key:
            prefix_keys = frozenset(self.unique_key(op) for op in prefix)
            ops = frozenset(op for op in ops if self.unique_key(op) not in prefix_keys)

        if self.curr_prev_constraint is not None:

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
                if self.curr_prev_constraint is not None and self.loop:
                    for k, f in self.curr_prev_constraint.items():
                        if any(not f(candidate[(i + k) % self.n], candidate[i]) for i in range(abs(k))):
                            break
                    else:
                        yield tuple(candidate)
                else:
                    yield tuple(candidate)
            else:
                yield from self._iter(prefix=candidate)



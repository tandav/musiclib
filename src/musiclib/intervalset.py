from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterator
import numpy as np

from musiclib import config
from musiclib.util.cache import Cached

Self = TypeVar('Self', bound='IntervalSet')


class IntervalSet(Cached):
    def __init__(self, intervals: frozenset[int]) -> None:
        if not isinstance(intervals, frozenset):
            raise TypeError(f'expected frozenset, got {type(intervals)}')
        self.intervals = intervals
        self.intervals_ascending = tuple(sorted(intervals))
        self.bits = ''.join('1' if i in intervals else '0' for i in range(12))
        self.names: frozenset[str] = config.intervals_to_names.get(intervals, frozenset())
        self.name_kinds = {name: config.kinds[name] for name in self.names}

    @classmethod
    def from_name(cls: type[Self], name: str) -> Self:
        return cls(config.name_to_intervals[name])

    @classmethod
    def from_bits(cls, bits: str) -> IntervalSet:
        return cls(frozenset(i for i, v in enumerate(bits) if int(v)))

    @classmethod
    def from_base12(cls, intervals: frozenset[str]) -> IntervalSet:
        return cls(frozenset(int(i, 12) for i in intervals))

    def __len__(self) -> int:
        return len(self.intervals)

    def __iter__(self) -> Iterator[int]:
        return iter(self.intervals_ascending)

    def __getnewargs__(self) -> tuple[frozenset[int]]:
        return (self.intervals,)

    def __repr__(self) -> str:
        return f"IntervalSet({' '.join(np.base_repr(i, 12) for i in self.intervals_ascending)})"

    # def _repr_svg_(self, **kwargs: Any) -> str:
    #     kwargs.setdefault('note_colors', {note: config.interval_colors[interval] for note, interval in self.note_to_interval.items()})
    #     kwargs.setdefault('title', f'{self.str_names}')
    #     kwargs.setdefault('classes', ('card', *self.intervalset.names))
    #     return Piano(**kwargs)._repr_svg_()

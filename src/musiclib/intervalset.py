from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Iterator
from musiclib.util.cache import Cached
import numpy as np


class IntervalSet(Cached):
    def __init__(self, intervals: frozenset[int]) -> None:
        if not isinstance(intervals, frozenset):
            raise TypeError(f'expected frozenset, got {type(intervals)}')
        self.intervals = intervals
        self.intervals_ascending = tuple(sorted(intervals))
        self.bits = ''.join('1' if i in intervals else '0' for i in range(12))

    def __iter__(self) -> Iterator[int]:
        return iter(self.intervals_ascending)
        
    @classmethod
    def from_bits(cls, bits: str) -> IntervalSet:
        return cls(frozenset(i for i, v in enumerate(bits) if int(v)))
    
    @classmethod
    def from_base12(cls, intervals: frozenset[str]) -> IntervalSet:
        return cls(frozenset(int(i, 12) for i in intervals))

    def __repr__(self) -> str:
        return f"IntervalSet({' '.join(np.base_repr(i, 12) for i in self.intervals)})"

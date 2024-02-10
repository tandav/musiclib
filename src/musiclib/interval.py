import functools
from typing import Self

import numpy as np

from musiclib.util.cache import Cached


@functools.total_ordering
class AbstractInterval(Cached):
    def __init__(self, interval: int) -> None:
        if not isinstance(interval, int):
            raise TypeError(f'expected int, got {type(interval)}')
        self.interval = interval % 12

    @classmethod
    def from_str(cls: type[Self], string: str) -> Self:
        if string == '':
            raise ValueError('interval string must not be empty')
        return cls(int(string, base=12))

    def __neg__(self: Self) -> Self:
        return self.__class__(-self.interval)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AbstractInterval):
            return False
        return self.interval == other.interval

    def __hash__(self) -> int:
        return hash(self.interval)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, AbstractInterval):
            raise TypeError
        return self.interval < other.interval

    def __getnewargs__(self) -> tuple[int]:
        return (self.interval,)

    def __str__(self) -> str:
        return np.base_repr(self.interval, base=12)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self})'

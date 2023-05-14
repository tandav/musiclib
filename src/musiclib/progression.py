from __future__ import annotations

import functools
import itertools
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Sequence
from typing import overload

from musiclib.chord import SpecificChord
from musiclib.note import SpecificNote
from musiclib.util.cache import Cached

CheckCallable = Callable[[SpecificChord, SpecificChord], bool]


class Progression(Cached, Sequence[SpecificChord]):
    def __init__(self, chords: tuple[SpecificChord, ...], /) -> None:
        if not all(isinstance(x, SpecificChord) for x in chords):
            raise TypeError('only SpecificChord items allowed')
        self.chords = chords

    @overload
    def __getitem__(self, i: int) -> SpecificChord:
        ...

    @overload
    def __getitem__(self, s: slice) -> Progression:
        ...

    def __getitem__(self, item: int | slice) -> SpecificChord | Sequence[SpecificChord]:
        if isinstance(item, slice):
            return Progression(self.chords[item])
        return self.chords[item]

    def __iter__(self) -> Iterator[SpecificChord]:
        return iter(self.chords)

    def __len__(self) -> int:
        return len(self.chords)

    def __repr__(self) -> str:
        return f'Progression{self.chords}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Progression):
            return NotImplemented
        return self.chords == other.chords

    def __hash__(self) -> int:
        return hash(self.chords)

    def are_all(self, checks__: Iterable[CheckCallable]) -> bool:
        return all(check(a, b) for a, b in itertools.pairwise(self) for check in checks__)

    def are_all_not(self, checks__: Iterable[CheckCallable]) -> bool:
        return all(not check(a, b) for a, b in itertools.pairwise(self) for check in checks__)

    @property
    def distance(self) -> int:
        n = len(self)
        return sum(abs(self[i] - self[(i + 1) % n]) for i in range(n))

    def transpose_unique_key(self, *, origin_name: bool = True) -> tuple[frozenset[int], ...] | tuple[int, tuple[frozenset[int], ...]]:
        origin = self[0][0]  # pylint: disable=unsubscriptable-object
        key = tuple(frozenset(note - origin for note in chord.notes) for chord in self)
        if origin_name:
            return origin.abstract.i, key
        return key

    def __add__(self, other: int) -> Progression:
        if not isinstance(other, int):
            raise TypeError('only adding integers is allowed (transposition)')
        return Progression(tuple(chord + other for chord in self))

    @functools.cached_property
    def transposed_to_C0(self) -> Progression:
        return self + (SpecificNote('C', 0) - self[0][0])  # pylint: disable=unsubscriptable-object

    def __getnewargs__(self) -> tuple[tuple[SpecificChord, ...]]:
        return (self.chords,)

from __future__ import annotations

import itertools

from musictool.chord import SpecificChord
from musictool.note import SpecificNote


class Progression(list):
    def __init__(self, iterable=(), /):
        iterable = list(iterable)
        if not all(isinstance(x, SpecificChord) for x in iterable):
            raise TypeError('only SpecificChord items allowed')
        super().__init__(iterable)

    def all(self, checks__):
        return all(check(a, b) for a, b in itertools.pairwise(self) for check in checks__)

    def all_not(self, checks__):
        return all(not check(a, b) for a, b in itertools.pairwise(self) for check in checks__)

    @property
    def distance(self):
        n = len(self)
        return sum(abs(self[i] - self[(i + 1) % n]) for i in range(n))

    @property
    def transpose_unique_key(self):
        origin = self[0].notes_ascending[0]
        return origin.abstract.i, tuple(frozenset(note - origin for note in chord.notes) for chord in self)

    def transpose(self, origin: SpecificNote = SpecificNote('C', 0)) -> Progression:
        return Progression(chord.transpose(origin) for chord in self)

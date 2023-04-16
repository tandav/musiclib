from __future__ import annotations

import functools
from typing import TYPE_CHECKING
from typing import overload

from musiclib import config
from musiclib.util.cache import Cached

if TYPE_CHECKING:
    from collections.abc import Iterable


@functools.total_ordering
class Note(Cached):
    """
    abstract note, no octave/key
    kinda music theoretic pitch-class
    """

    def __init__(self, name: str) -> None:
        """param name: one of CdDeEFfGaAbB"""
        self.name = name
        self.i = config.note_i[name]
        self.is_black = config.is_black[name]

    @classmethod
    def from_i(cls, i: int) -> Note:
        return cls(config.chromatic_notes[i % 12])

    def __repr__(self) -> str:
        return f'Note(name={self.name})'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, Note):
            return self.name == other.name
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.i <= config.note_i[other]
        if isinstance(other, Note):
            return self.i <= other.i
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)

    def __add__(self, other: int) -> Note:
        return Note.from_i(self.i + other)

    @overload
    def __sub__(self, other: Note) -> int:
        ...

    @overload
    def __sub__(self, other: int) -> Note:
        ...

    def __sub__(self, other: Note | int) -> int | Note:
        """
        kinda constraint (maybe it will be changed later):
            if you're computing distance between abstract notes - then self considered above other
            G - C == 7 # C0 G0
            C - G == 5 # G0 C1
        """
        if isinstance(other, Note):
            if other.i <= self.i:
                return self.i - other.i
            return 12 + self.i - other.i
        if isinstance(other, int):
            return self + (-other)
        return None  # type: ignore[unreachable]

    def __getnewargs__(self) -> tuple[str]:
        return (self.name,)


@functools.total_ordering
class SpecificNote(Cached):
    def __init__(self, abstract: Note | str, octave: int) -> None:
        if isinstance(abstract, str):
            abstract = Note(abstract)
        self.abstract = abstract
        self.is_black = abstract.is_black
        self.octave = octave
        self.i: int = (octave + 1) * 12 + self.abstract.i  # this is also midi_code
        self._key = self.abstract, self.octave

    @classmethod
    def from_i(cls, i: int) -> SpecificNote:
        div, mod = divmod(i, 12)
        return cls(Note(config.chromatic_notes[mod]), octave=div - 1)

    @classmethod
    def from_str(cls, string: str) -> SpecificNote:
        return cls(Note(string[0]), int(string[1:]))

    def __repr__(self) -> str:
        return f'{self.abstract.name}{self.octave}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SpecificNote):
            return NotImplemented
        return self._key == other._key

    def __hash__(self) -> int:
        return hash(self._key)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SpecificNote):
            return NotImplemented
        return self.i < other.i

    @overload
    def __sub__(self, other: SpecificNote) -> int:
        ...

    @overload
    def __sub__(self, other: int) -> SpecificNote:
        ...

    # @functools.cache
    def __sub__(self, other: SpecificNote | int) -> int | SpecificNote:
        if isinstance(other, SpecificNote):  # distance between notes
            return self.i - other.i
        if isinstance(other, int):  # subtract semitones
            return self + (-other)
        raise TypeError(f'SpecificNote.__sub__ supports only SpecificNote | int, got {type(other)}')

    def __add__(self, other: int) -> SpecificNote:
        """C + 7 = G"""
        return SpecificNote.from_i(self.i + other)

    @staticmethod
    def to_abstract(notes: Iterable[SpecificNote]) -> frozenset[Note]:
        return frozenset(note.abstract for note in notes)

    def __getnewargs__(self) -> tuple[Note, int]:
        return self.abstract, self.octave


WHITE_NOTES = frozenset(map(Note, 'CDEFGAB'))
BLACK_NOTES = frozenset(map(Note, 'defab'))

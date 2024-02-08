from __future__ import annotations

import functools
from typing import overload

from musiclib import config
from musiclib.interval import AbstractInterval
from musiclib.util.cache import Cached

_note_i = {note: i for i, note in enumerate(config.chromatic_notes)}
_is_black = {note: bool(int(x)) for note, x in zip(config.chromatic_notes, '010100101010', strict=True)}


@functools.total_ordering
class Note(Cached):
    def __init__(self, name: str) -> None:
        self.name = name
        self.i = _note_i[name]
        self.is_black = _is_black[name]

    @classmethod
    def from_i(cls, i: int) -> Note:
        return cls(config.chromatic_notes[i % 12])

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'Note({self.name!r})'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, Note):
            return self.name == other.name
        return False

    def __lt__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.i <= _note_i[other]
        if isinstance(other, Note):
            return self.i <= other.i
        raise TypeError

    def __hash__(self) -> int:
        return hash(self.name)

    @overload
    def __add__(self, other: int) -> Note:
        ...

    @overload
    def __add__(self, other: AbstractInterval) -> Note:
        ...

    def __add__(self, other: int | AbstractInterval) -> Note:
        if isinstance(other, AbstractInterval):
            return Note.from_i(self.i + other.interval)
        if isinstance(other, int):
            return Note.from_i(self.i + other)
        raise TypeError(f'Note.__add__ supports only int | AbstractInterval, got {type(other)}')

    @overload
    def __sub__(self, other: Note) -> AbstractInterval:
        ...

    @overload
    def __sub__(self, other: AbstractInterval) -> Note:
        ...

    @overload
    def __sub__(self, other: int) -> Note:
        ...

    def __sub__(self, other: Note | AbstractInterval | int) -> AbstractInterval | Note:
        if isinstance(other, Note):
            if other.i <= self.i:
                return AbstractInterval(self.i - other.i)
            return AbstractInterval(12 + self.i - other.i)
        if isinstance(other, AbstractInterval):
            return self + (-other)
        if isinstance(other, int):
            return self + (-other)
        raise TypeError(f'Note.__sub__ supports only Note | AbstractInterval | int, got {type(other)}')

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

    def __str__(self) -> str:
        return f'{self.abstract.name}{self.octave}'

    def __repr__(self) -> str:
        return f'SpecificNote({self.abstract.name!r}, {self.octave})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SpecificNote):
            return False
        return self._key == other._key

    def __hash__(self) -> int:
        return hash(self._key)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SpecificNote):
            raise TypeError
        return self.i < other.i

    @overload
    def __sub__(self, other: SpecificNote) -> int:
        ...

    @overload
    def __sub__(self, other: int) -> SpecificNote:
        ...

    def __sub__(self, other: SpecificNote | int) -> int | SpecificNote:
        if isinstance(other, SpecificNote):  # distance between notes
            return self.i - other.i
        if isinstance(other, int):  # subtract semitones
            return self + (-other)
        raise TypeError(f'SpecificNote.__sub__ supports only SpecificNote | int, got {type(other)}')

    def __add__(self, other: int) -> SpecificNote:
        return SpecificNote.from_i(self.i + other)

    def __getnewargs__(self) -> tuple[Note, int]:
        return self.abstract, self.octave

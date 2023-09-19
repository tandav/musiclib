from __future__ import annotations

import itertools
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import TypeVar
from typing import overload

from musiclib.config import RED
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.util import typeguards
from musiclib.util.cache import Cached

if TYPE_CHECKING:
    from collections.abc import Iterator


Self = TypeVar('Self', bound='NoteSet')


class NoteSet(Cached):
    name_to_intervals_key: ClassVar[dict[str, frozenset[frozenset[int]]]] = {
        'natural': frozenset({
            frozenset({0, 1, 3, 5, 6, 8, 10}),
            frozenset({0, 1, 3, 5, 7, 8, 10}),
            frozenset({0, 2, 3, 5, 7, 8, 10}),
            frozenset({0, 2, 3, 5, 7, 9, 10}),
            frozenset({0, 2, 4, 5, 7, 9, 10}),
            frozenset({0, 2, 4, 5, 7, 9, 11}),
            frozenset({0, 2, 4, 6, 7, 9, 11}),
        }),
        'harmonic': frozenset({
            frozenset({0, 1, 3, 4, 6, 8, 9}),
            frozenset({0, 1, 3, 5, 6, 9, 10}),
            frozenset({0, 1, 4, 5, 7, 8, 10}),
            frozenset({0, 2, 3, 5, 7, 8, 11}),
            frozenset({0, 2, 3, 6, 7, 9, 10}),
            frozenset({0, 2, 4, 5, 8, 9, 11}),
            frozenset({0, 3, 4, 6, 7, 9, 11}),
        }),
        'melodic': frozenset({
            frozenset({0, 1, 3, 4, 6, 8, 10}),
            frozenset({0, 1, 3, 5, 7, 9, 10}),
            frozenset({0, 2, 3, 5, 6, 8, 10}),
            frozenset({0, 2, 3, 5, 7, 9, 11}),
            frozenset({0, 2, 4, 5, 7, 8, 10}),
            frozenset({0, 2, 4, 6, 7, 9, 10}),
            frozenset({0, 2, 4, 6, 8, 9, 11}),
        }),
        'pentatonic': frozenset({
            frozenset({0, 2, 4, 7, 9}),
            frozenset({0, 2, 5, 7, 9}),
            frozenset({0, 2, 5, 7, 10}),
            frozenset({0, 3, 5, 7, 10}),
            frozenset({0, 3, 5, 8, 10}),
        }),
        'sudu': frozenset({
            frozenset({0, 1, 3, 5, 8, 10}),
            frozenset({0, 2, 3, 5, 7, 10}),
            frozenset({0, 2, 4, 5, 7, 9}),
            frozenset({0, 2, 4, 7, 9, 11}),
            frozenset({0, 2, 5, 7, 9, 10}),
            frozenset({0, 3, 5, 7, 8, 10}),
        }),
    }
    intervals_key_to_name: ClassVar[dict[frozenset[frozenset[int]], str]] = {v: k for k, v in name_to_intervals_key.items()}
    notes: frozenset[Note]
    intervals_ascending: tuple[int, ...] | tuple[()]

    def __init__(self, notes: frozenset[Note]) -> None:
        if not isinstance(notes, frozenset):
            raise TypeError(f'expected frozenset, got {type(notes)}')

        # TODO: try to use just `self.notes = notes`
        if len(notes) == 0:
            self.notes = frozenset()
        elif typeguards.is_frozenset_of_note(notes):
            self.notes = notes
        else:
            raise TypeError('expected frozenset of Note')

        self.notes_ascending = tuple(sorted(self.notes))
        self.note_to_intervals = {note: frozenset(note - other for other in self.notes) for note in self.notes}
        self.intervals_key = frozenset(self.note_to_intervals.values())
        self.name = self.__class__.intervals_key_to_name.get(self.intervals_key)
        self._note_i = {note: i for i, note in enumerate(self.notes_ascending)}

    @classmethod
    def from_str(cls: type[Self], string: str) -> Self:
        return cls(frozenset(Note(note) for note in string))

    @overload
    def add_note(self, note: SpecificNote, steps: int) -> SpecificNote:
        ...

    @overload
    def add_note(self, note: Note, steps: int) -> Note:
        ...

    def add_note(self, note: Note | SpecificNote, steps: int) -> Note | SpecificNote:
        if len(self) == 0:
            raise NotImplementedError('cannot add notes using empty noteset')
        notes = self.notes_ascending
        if isinstance(note, Note):
            return notes[(notes.index(note) + steps) % len(notes)]
        if isinstance(note, SpecificNote):
            octaves, i = divmod(self.notes_ascending.index(note.abstract) + steps, len(self.notes))
            return SpecificNote(self.notes_ascending[i], octave=note.octave + octaves)
        raise TypeError

    def subtract(self, left: Note | SpecificNote, right: Note | SpecificNote) -> int:
        if type(left) is type(right) is Note:
            return (self._note_i[left] - self._note_i[right]) % len(self)
        if type(left) is type(right) is SpecificNote:
            return self._note_i[left.abstract] - self._note_i[right.abstract] + len(self) * (left.octave - right.octave)
        raise TypeError('left and right should be either Note or SpecificNote')

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NoteSet):
            return NotImplemented
        return self.notes == other.notes

    def __hash__(self) -> int:
        return hash(self.notes)

    def __len__(self) -> int:
        return len(self.notes)

    def __getitem__(self, item: int) -> Note:
        return self.notes_ascending[item]

    def __iter__(self) -> Iterator[Note]:
        return iter(self.notes_ascending)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Note):
            return NotImplemented
        return item in self.notes

    def __le__(self, other: object) -> bool:
        if not isinstance(other, NoteSet):
            return NotImplemented
        return self.notes <= other.notes

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, NoteSet):
            return NotImplemented
        return other.notes <= self.notes

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, NoteSet):
            return NotImplemented
        return self.notes < other.notes

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, NoteSet):
            return NotImplemented
        return other.notes < self.notes

    def __str__(self) -> str:
        return ''.join(note.name for note in self)

    def __repr__(self) -> str:
        return f'NoteSet(notes={self.notes})'

    def _repr_svg_(self, **kwargs: Any) -> str:
        from musiclib.svg.piano import Piano  # hack to fix circular import
        kwargs.setdefault('title', str(self))
        kwargs.setdefault('note_colors', {note: RED for note in self})
        kwargs.setdefault('classes', ('card',))
        return Piano(**kwargs)._repr_svg_()

    def __getnewargs__(self) -> tuple[frozenset[Note]]:
        return (self.notes,)


def subsets(noteset: NoteSet, min_notes: int = 1) -> frozenset[NoteSet]:
    out = set()
    for n_subset in range(min_notes, len(noteset) + 1):
        for notes in itertools.combinations(noteset, n_subset):
            out.add(NoteSet(frozenset(notes)))
    return frozenset(out)

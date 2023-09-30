from __future__ import annotations

import itertools
import random
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeVar
from typing import overload

from musiclib import config
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.util.cache import Cached

if TYPE_CHECKING:
    from collections.abc import Iterator


Self = TypeVar('Self', bound='NoteSet')


class NoteSet(Cached):
    def __init__(self, notes: frozenset[Note]) -> None:
        if not isinstance(notes, frozenset):
            raise TypeError(f'expected frozenset, got {type(notes)}')
        self.notes = notes
        self.notes_ascending = tuple(sorted(self.notes))
        self.note_to_intervals = {left: frozenset(right - left for right in self.notes) for left in self.notes}
        self.intervals_key = frozenset(self.note_to_intervals.values())
        self.name = config.intervals_key_to_name.get(self.intervals_key)
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
        return f"NoteSet('{self}')"

    def _repr_svg_(self, **kwargs: Any) -> str:
        from musiclib.svg.piano import Piano  # hack to fix circular import
        kwargs.setdefault('title', str(self))
        kwargs.setdefault('note_colors', {note: config.RED for note in self})
        kwargs.setdefault('classes', ('card',))
        return Piano(**kwargs)._repr_svg_()

    def __getnewargs__(self) -> tuple[frozenset[Note]]:
        return (self.notes,)


class SpecificNoteSet(Cached):
    def __init__(self, notes: frozenset[SpecificNote]) -> None:
        if not isinstance(notes, frozenset):
            raise TypeError(f'expected frozenset, got {type(notes)}')
        self.notes = notes
        self.noteset = NoteSet(frozenset(note.abstract for note in notes))
        self.notes_ascending = tuple(sorted(notes))
        self.intervals = tuple(note - self.notes_ascending[0] for note in self.notes_ascending)  # from lowest note

    @classmethod
    def random(
        cls,
        n_notes: int | None = None,
        notes: frozenset[Note] = frozenset({Note(n) for n in config.chromatic_notes}),  # noqa: B008
        octaves: frozenset[int] = frozenset({3, 4, 5}),
    ) -> SpecificNoteSet:
        if n_notes is None:
            n_notes = random.randint(2, 5)
        notes_space = tuple(
            SpecificNote(note, octave)
            for note, octave in itertools.product(notes, octaves)
        )
        return cls(frozenset(random.sample(notes_space, n_notes)))

    @classmethod
    def from_str(cls, string: str) -> SpecificNoteSet:
        notes_ = string.split('_')
        if len(notes_) != len(set(notes_)):
            raise ValueError('SpecificNoteSet with non unique notes are not supported')
        notes = frozenset(SpecificNote.from_str(note) for note in notes_)
        return cls(notes)

    def notes_combinations(self) -> Iterator[tuple[SpecificNote, SpecificNote]]:
        yield from itertools.combinations(self.notes_ascending, 2)

    def find_intervals(self, interval: int) -> tuple[tuple[SpecificNote, SpecificNote], ...]:
        return tuple((n, m) for n, m in self.notes_combinations() if abs(m - n) == interval)

    def transpose_to_note(self, note: SpecificNote) -> SpecificNoteSet:
        if len(self) == 0:
            return self
        return self + (note - self[0])

    def __len__(self) -> int:
        return len(self.notes)

    def __getitem__(self, item: int) -> SpecificNote:
        return self.notes_ascending[item]

    def __iter__(self) -> Iterator[SpecificNote]:
        return iter(self.notes_ascending)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, SpecificNote):
            return NotImplemented
        return item in self.notes

    def __str__(self) -> str:
        return '_'.join(str(note) for note in self.notes_ascending)

    def __repr__(self) -> str:
        return '_'.join(repr(note) for note in self.notes_ascending)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SpecificNoteSet):
            return NotImplemented
        return self.notes == other.notes

    def __hash__(self) -> int:
        return hash(self.notes)

    def __sub__(self, other: SpecificNoteSet) -> int:
        return sum(abs(a - b) for a, b in zip(self, other, strict=True))

    def __add__(self, other: int) -> SpecificNoteSet:
        """transpose"""
        if not isinstance(other, int):
            raise TypeError('only adding integers is allowed (transposition)')
        return SpecificNoteSet(frozenset(note + other for note in self))

    def __getnewargs__(self) -> tuple[frozenset[SpecificNote]]:
        return (self.notes,)

    def _repr_svg_(self, **kwargs: Any) -> str:
        from musiclib.noterange import NoteRange
        from musiclib.svg.piano import Piano
        kwargs.setdefault('noterange', NoteRange(self[0], self[-1]) if self.notes else None)
        kwargs.setdefault('classes', ('card',))
        kwargs.setdefault('title', repr(self))
        kwargs.setdefault('note_colors', dict.fromkeys(self.notes, config.RED))
        kwargs.setdefault('squares', {note: {'text': str(note), 'text_size': '8'} for note in self})
        return Piano(**kwargs)._repr_svg_()


def subsets(noteset: NoteSet, min_notes: int = 1) -> frozenset[NoteSet]:
    out = set()
    for n_subset in range(min_notes, len(noteset) + 1):
        for notes in itertools.combinations(noteset, n_subset):
            out.add(NoteSet(frozenset(notes)))
    return frozenset(out)


class ComparedNoteSets(Cached):
    """
    this is compared scale
    local terminology: left scale is compared to right
    left is kinda parent, right is kinda child
    """

    def __init__(self, left: NoteSet, right: NoteSet) -> None:
        if not (isinstance(left, NoteSet) and isinstance(right, NoteSet)):
            raise TypeError(f'expected NoteSet, got {type(left)} and {type(right)}')
        self.left = left
        self.right = right
        self.key = left, right
        self.shared_notes = frozenset(left.notes) & frozenset(right.notes)
        self.new_notes = frozenset(right.notes) - frozenset(left.notes)
        self.del_notes = frozenset(left.notes) - frozenset(right.notes)

    def _repr_svg_(self, **kwargs: Any) -> str:
        from musiclib.svg.piano import Piano
        kwargs.setdefault(
            'note_colors',
            dict.fromkeys(self.del_notes, config.RED) |
            dict.fromkeys(self.new_notes, config.GREEN) |
            dict.fromkeys(self.shared_notes, config.BLUE),
        )
        kwargs.setdefault('classes', ('card',))
        kwargs.setdefault('title', f'{self.left} | {self.right}')
        return Piano(**kwargs)._repr_svg_()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComparedNoteSets):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return f'ComparedNoteSets({self.left} | {self.right})'

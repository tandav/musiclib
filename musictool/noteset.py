from __future__ import annotations

import itertools
import random
from collections.abc import Sequence
from typing import Type
from typing import TypeVar
from typing import no_type_check
from typing import overload

import pipe21 as P

from musictool import config
from musictool.note import AnyNote
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.note import str_to_note
from musictool.piano import Piano
from musictool.util import typeguards
from musictool.util.cache import Cached


@no_type_check
def bits_to_intervals(bits: str) -> frozenset[int]:
    return (
        bits
        | P.Map(int)
        | P.Pipe(enumerate)
        | P.Pipe(lambda it: itertools.islice(it, 1, None))
        | P.FilterValues()
        | P.Keys()
        | P.Pipe(frozenset)
    )


def intervals_to_bits(intervals: frozenset[int]) -> str:
    bits = ['0'] * 12
    bits[0] = '1'
    for i in intervals:
        bits[i] = '1'
    return ''.join(bits)


Self = TypeVar('Self', bound='NoteSet')


class NoteSet(Cached):
    """
    an unordered set of notes
    root note is optional
    notes w/o root has no intervals

    hierarchy of classes:
    NoteSet
        NotesWithRoot
            Scale
            Chord
    """
    intervals_to_name: dict[frozenset[int], str] = {}
    name_to_intervals: dict[str, frozenset[int]] = {}

    notes: frozenset[Note]
    root: Note | None

    def __init__(
        self,
        notes: frozenset[str | Note],
        *,
        root: str | Note | None = None,
    ):
        if not isinstance(notes, frozenset):
            raise TypeError(f'expected frozenset, got {type(notes)}')

        if len(notes) == 0:
            raise ValueError('notes should be not empty')

        if typeguards.is_frozenset_of_str(notes):
            self.notes = frozenset(Note(note) for note in notes)
        elif typeguards.is_frozenset_of_note(notes):
            self.notes = notes
        else:
            raise TypeError

        self.notes_octave_fit = tuple(sorted(self.notes))

        if root is None:
            self.root = root
            self.notes_ascending = self.notes_octave_fit
        else:
            if root not in self.notes:
                raise KeyError('root should be one of notes')

            if isinstance(root, Note):
                self.root = root
            elif isinstance(root, str):
                self.root = Note(root)
            else:
                raise TypeError('root type should be str | Note | None')

            root_i = self.notes_octave_fit.index(self.root)
            self.notes_ascending = self.notes_octave_fit[root_i:] + self.notes_octave_fit[:root_i]
            self.intervals_ascending = tuple(note - self.root for note in self.notes_ascending)
            self.intervals = frozenset(self.intervals_ascending[1:])
            self.bits = intervals_to_bits(self.intervals)
            self.name = self.__class__.intervals_to_name.get(self.intervals)

        self.key = self.notes, self.root
        self.note_i = {note: i for i, note in enumerate(self.notes_ascending)}
        self.increments = {a: b - a for a, b in itertools.pairwise(self.notes_ascending + (self.notes_ascending[0],))}
        self.decrements = {b: -(b - a) for a, b in itertools.pairwise((self.notes_ascending[-1],) + self.notes_ascending)}
        self.html_classes: tuple[str, ...] = ('card',)

    @property
    def rootless(self): return NoteSet(self.notes)

    def transpose_to(self, note: Note) -> NoteSet:
        if self.root is None:
            raise ValueError('noteset should have root to be transposed')
        return NoteSet.from_intervals(self.intervals, note)

    @classmethod
    def from_name(cls: Type[Self], root: str | Note, name: str) -> Self:
        if isinstance(root, str):
            root = Note(root)
        notes = frozenset(root + interval for interval in cls.name_to_intervals[name]) | {root}
        return cls(notes, root=root)

    @classmethod
    def from_intervals(cls: Type[Self], intervals: frozenset[int], root: str | Note) -> Self:
        if isinstance(root, str):
            root = Note(root)
        return cls(frozenset(root + interval for interval in intervals) | {root}, root=root)

    @classmethod
    def random(cls: Type[Self], n_notes: int | None = None) -> Self:
        if n_notes is None:
            n_notes = random.randint(2, 5)
        notes = frozenset(random.sample(config.chromatic_notes, n_notes))
        return cls(notes)

    @classmethod
    def from_str(cls: Type[Self], string: str) -> Self:
        notes, _, root_ = string.partition('/')
        root = Note(root_) if root_ else None
        return cls(frozenset(Note(note) for note in notes), root=root)

    @overload
    def add_note(self, note: str, steps: int) -> Note | SpecificNote: ...
    @overload
    def add_note(self, note: SpecificNote, steps: int) -> SpecificNote: ...
    @overload
    def add_note(self, note: Note, steps: int) -> Note: ...

    def add_note(self, note: AnyNote, steps: int) -> Note | SpecificNote:
        notes = self.notes_ascending
        if type(note) is str:
            note = str_to_note(note)
        if type(note) is Note:
            return notes[(notes.index(note) + steps) % len(notes)]
        elif type(note) is SpecificNote:
            octaves, i = divmod(self.notes_octave_fit.index(note.abstract) + steps, len(self.notes))
            return SpecificNote(self.notes_octave_fit[i], octave=note.octave + octaves)
        else:
            raise TypeError

    def subtract(self, left: AnyNote, right: AnyNote) -> int:
        if type(left) is str: left = str_to_note(left)
        if type(right) is str: right = str_to_note(right)

        if type(left) is type(right) is Note:
            return (self.note_i[left] - self.note_i[right]) % len(self)
        elif type(left) is type(right) is SpecificNote:
            return self.note_i[left.abstract] - self.note_i[right.abstract] + len(self) * (left.octave - right.octave)
        else:
            raise TypeError('left and right should be either Note or SpecificNote (or str representation)')

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)
    def __len__(self): return len(self.notes)
    def __getitem__(self, item): return self.notes_ascending[item]
    def __iter__(self): return iter(self.notes_ascending)
    def __contains__(self, item: str | Note) -> bool: return item in self.notes
    def __le__(self, other): return self.notes <= other
    def __ge__(self, other): return other <= self.notes

    def __repr__(self):
        _ = ''.join(note.name for note in self)
        if self.root is not None:
            _ += f'/{self.root.name}'
        return _

    def to_piano_image(self):
        return Piano(notes=self.notes)._repr_svg_()

    def with_html_classes(self, classes: tuple[str, ...]) -> str:
        prev = self.html_classes
        self.html_classes = prev + classes
        r = self._repr_html_()
        self.html_classes = prev
        return r

    def _repr_html_(self) -> str:
        notes_str = ''.join(note.name for note in self)
        root_str = f'/{self.root.name}' if self.root is not None else ''
        return f"""
        <div class='{' '.join(self.html_classes)}'>
        <span class='card_header'><h3>{notes_str}{root_str}</h3></span>
        {self.to_piano_image()}
        </div>
        """

    def __getnewargs_ex__(self):
        return (self.notes,), {'root': self.root}


CHROMATIC_NOTESET = NoteSet(frozenset(config.chromatic_notes))


class NoteRange(Sequence[SpecificNote]):
    def __init__(
        self,
        start: SpecificNote | str,
        stop: SpecificNote | str,
        noteset: NoteSet = CHROMATIC_NOTESET,
    ):
        if isinstance(start, str):
            start = SpecificNote.from_str(start)
        if isinstance(stop, str):
            stop = SpecificNote.from_str(stop)

        """both ends included"""
        if start > stop:
            raise ValueError('start should be less than stop')

        if not {start.abstract, stop.abstract} <= noteset.notes:
            raise KeyError('start and stop notes should be in the noteset')

        self.start = start
        self.stop = stop
        self.noteset = noteset
        self._key = self.start, self.stop, self.noteset

    def _getitem_int(self, item: int) -> SpecificNote:
        if 0 <= item < len(self):
            q = self.noteset.add_note(self.start, item)
            return q
        elif -len(self) <= item < 0: return self.noteset.add_note(self.stop, item + 1)
        else: raise IndexError('index out of range')

    @overload
    def __getitem__(self, i: int) -> SpecificNote: ...

    @overload
    def __getitem__(self, s: slice) -> NoteRange: ...

    def __getitem__(self, item: int | slice) -> SpecificNote | NoteRange:
        if isinstance(item, int): return self._getitem_int(item)
        elif isinstance(item, slice):
            if not 0 <= item.start <= item.stop <= len(self):
                raise IndexError('NoteRange slice is out of range')
            return NoteRange(self._getitem_int(item.start), self._getitem_int(item.stop), self.noteset)
        else: raise TypeError(f'NoteRange indices must be integers or slices, got {type(item)}')

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, SpecificNote):
            return False
        return item.abstract in self.noteset and self.start <= item <= self.stop

    def __iter__(self): return (self[i] for i in range(len(self)))
    def __repr__(self): return f'NoteRange({self.start}, {self.stop}, noteset={self.noteset})'
    def __len__(self): return self.noteset.subtract(self.stop, self.start) + 1
    def __eq__(self, other): return self._key == other._key
    def __hash__(self): return hash(self._key)

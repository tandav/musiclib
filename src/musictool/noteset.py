from __future__ import annotations

import itertools
import random
from collections.abc import Iterator
from typing import TypeVar
from typing import no_type_check
from typing import overload

import pipe21 as P

from musictool import config
from musictool.card import Card
from musictool.config import RED
from musictool.note import AnyNote
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.note import str_to_note
from musictool.util import typeguards
from musictool.util.cache import Cached


@no_type_check
def bits_to_intervals(bits: str) -> frozenset[int]:
    return (
        bits
        | P.Map(int)
        | P.Pipe(enumerate)
        | P.FilterValues()
        | P.Keys()
        | P.Pipe(frozenset)
    )


def intervals_to_bits(intervals: frozenset[int]) -> str:
    bits = ['0'] * 12
    for i in intervals:
        bits[i] = '1'
    return ''.join(bits)


Self = TypeVar('Self', bound='NoteSet')


class NoteSet(Cached, Card):
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
    intervals_ascending: tuple[int, ...] | tuple[()]

    def __init__(
        self,
        notes: frozenset[Note],
        *,
        root: Note | None = None,
    ):
        if not isinstance(notes, frozenset):
            raise TypeError(f'expected frozenset, got {type(notes)}')

        if len(notes) == 0:
            self.notes = frozenset()
        elif typeguards.is_frozenset_of_note(notes):
            self.notes = notes
        else:
            raise TypeError('expected frozenset of Note')

        self.notes_octave_fit = tuple(sorted(self.notes))

        if root is None:
            self.root = root
            self.notes_ascending = self.notes_octave_fit
            self.intervals_ascending = ()
        elif not isinstance(root, Note):
            raise TypeError('root type should be Note | None')
        elif root not in self.notes:
            raise KeyError('root should be one of notes')
        else:
            self.root = root
            root_i = self.notes_octave_fit.index(self.root)
            self.notes_ascending = self.notes_octave_fit[root_i:] + self.notes_octave_fit[:root_i]
            self.intervals_ascending = tuple(note - self.root for note in self.notes_ascending)
        self.intervals = frozenset(self.intervals_ascending)
        self.note_to_interval = dict(zip(self.notes_ascending, self.intervals_ascending))
        self.bits = intervals_to_bits(self.intervals)
        self.name = self.__class__.intervals_to_name.get(self.intervals)

        self.key = self.notes, self.root
        self.note_i = {note: i for i, note in enumerate(self.notes_ascending)}

    @property
    def rootless(self) -> NoteSet:
        return NoteSet(self.notes)

    def with_root(self, root: Note) -> NoteSet:
        if len(self) == 0:
            raise NotImplementedError('cannot add root to empty noteset')
        if not isinstance(root, Note):
            raise TypeError('root type should be Note')
        if root not in self.notes:
            raise KeyError('root should be one of notes')
        return NoteSet(self.notes, root=root)

    def transpose_to(self, note: Note) -> NoteSet:
        if self.root is None:
            raise ValueError('noteset should have root to be transposed')
        return NoteSet.from_intervals(self.intervals, note)

    @classmethod
    def from_name(cls: type[Self], root: str | Note, name: str) -> Self:
        if isinstance(root, str):
            root = Note(root)
        notes = frozenset(root + interval for interval in cls.name_to_intervals[name])
        return cls(notes, root=root)

    @classmethod
    def from_intervals(cls: type[Self], intervals: frozenset[int], root: str | Note | None) -> Self:
        if root is None:
            return cls(frozenset(), root=root)
        if isinstance(root, str):
            root = Note(root)
        return cls(frozenset(root + interval for interval in intervals), root=root)

    @classmethod
    def random(cls: type[Self], n_notes: int | None = None) -> Self:
        if n_notes is None:
            n_notes = random.randint(2, 5)
        notes = frozenset(map(Note, random.sample(config.chromatic_notes, n_notes)))
        return cls(notes)

    @classmethod
    def from_str(cls: type[Self], string: str) -> Self:
        notes, _, root_ = string.partition('/')
        kw = {'root': Note(root_)} if root_ else {}
        return cls(frozenset(Note(note) for note in notes), **kw)

    @overload
    def add_note(self, note: str, steps: int) -> Note | SpecificNote:
        ...

    @overload
    def add_note(self, note: SpecificNote, steps: int) -> SpecificNote:
        ...

    @overload
    def add_note(self, note: Note, steps: int) -> Note:
        ...

    def add_note(self, note: AnyNote, steps: int) -> Note | SpecificNote:
        if len(self) == 0:
            raise NotImplementedError('cannot add notes using empty noteset')
        notes = self.notes_ascending
        if isinstance(note, str):
            note = str_to_note(note)
        if isinstance(note, Note):
            return notes[(notes.index(note) + steps) % len(notes)]
        elif isinstance(note, SpecificNote):
            octaves, i = divmod(self.notes_octave_fit.index(note.abstract) + steps, len(self.notes))
            return SpecificNote(self.notes_octave_fit[i], octave=note.octave + octaves)
        else:
            raise TypeError

    def subtract(self, left: AnyNote, right: AnyNote) -> int:
        if isinstance(left, str):
            left = str_to_note(left)
        if isinstance(right, str):
            right = str_to_note(right)

        if type(left) is type(right) is Note:
            return (self.note_i[left] - self.note_i[right]) % len(self)
        elif type(left) is type(right) is SpecificNote:
            return self.note_i[left.abstract] - self.note_i[right.abstract] + len(self) * (left.octave - right.octave)
        else:
            raise TypeError('left and right should be either Note or SpecificNote (or str representation)')

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NoteSet):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

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

    def __repr__(self) -> str:
        x = ''.join(note.name for note in self)
        if self.root is not None:
            return f'{x}/{self.root.name}'
        return x

    def to_piano_image(self) -> str:
        from musictool.piano import Piano  # hack to fix circular import
        return Piano(note_colors={note: RED for note in self})._repr_svg_()

    def _repr_html_(
        self,
        html_classes: tuple[str, ...] = (),
        title: str | None = None,
        subtitle: str | None = None,
        header_href: str | None = None,
        background_color: str | None = None,
    ) -> str:
        return self.repr_card(
            html_classes=html_classes,
            title=title or repr(self),
            subtitle=subtitle,
            header_href=header_href,
            background_color=background_color,
            piano_html=self.to_piano_image(),
        )

    def __getnewargs_ex__(self) -> tuple[tuple[frozenset[Note]], dict[str, Note | None]]:
        return (self.notes,), {'root': self.root}


def subsets(noteset: NoteSet, min_notes: int = 1) -> frozenset[NoteSet]:
    out = set()
    for n_subset in range(min_notes, len(noteset) + 1):
        for notes in itertools.combinations(noteset, n_subset):
            out.add(NoteSet(frozenset(notes)))
    return frozenset(out)

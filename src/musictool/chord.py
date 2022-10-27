from __future__ import annotations

import functools
import itertools
import random
from collections.abc import Iterator

from musictool import config
from musictool.card import Card
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noteset import NoteSet
from musictool.util.cache import Cached


class Chord(NoteSet):
    intervals_to_name = {
        # triads
        frozenset({0, 4, 7}): 'major',
        frozenset({0, 3, 7}): 'minor',
        frozenset({0, 3, 6}): 'diminished',
        # 7th
        frozenset({0, 4, 7, 11}): 'maj7',
        frozenset({0, 4, 7, 10}): '7',
        frozenset({0, 3, 7, 10}): 'min7',
        frozenset({0, 3, 6, 10}): 'half-dim7',
        frozenset({0, 3, 6, 9}): 'dim7',
        # 6th
        frozenset({0, 4, 7, 9}): '6',
        frozenset({0, 3, 7, 9}): 'm6',
        # etc
        frozenset({0, 4, 8}): 'aug',
        frozenset({0, 2, 7}): 'sus2',
        frozenset({0, 5, 7}): 'sus4',
    }
    name_to_intervals = {v: k for k, v in intervals_to_name.items()}
    root: Note
    name: str

    def __init__(self, notes: frozenset[Note], *, root: Note):
        if root is None:
            raise TypeError('Chord requires root note. Use NoteSet if there is no root')
        super().__init__(notes, root=root)

    def _repr_html_(
        self,
        html_classes: tuple[str, ...] = ('card',),
        title: str | None = None,
        subtitle: str | None = None,
        header_href: str | None = None,
        background_color: str | None = None,
    ) -> str:
        return self.repr_card(
            html_classes=html_classes,
            title=title or f'{self.root.name} {self.name}',
            subtitle=subtitle,
            header_href=header_href,
            background_color=background_color,
            piano_html=self.to_piano_image(),
        )


class SpecificChord(Cached, Card):
    def __init__(
        self,
        notes: frozenset[SpecificNote],
        *,
        root: str | Note | None = None,
    ):
        if not isinstance(notes, frozenset):
            raise TypeError(f'expected frozenset, got {type(notes)}')

        if isinstance(root, str):
            root = Note(root)

        notes_abstract = SpecificNote.to_abstract(notes)
        if root is not None and root not in notes_abstract:
            raise KeyError('root should be one of notes')

        self.notes = notes
        self.root = root
        self.abstract = Chord(notes_abstract, root=root) if root is not None else NoteSet(notes_abstract)
        self.root_specific = frozenset(note for note in notes if note.abstract == root) if root is not None else frozenset()

        self.notes_ascending = tuple(sorted(notes))
        self.intervals = tuple(note - self.notes_ascending[0] for note in self.notes_ascending)  # from lowest note
        self.key = self.notes, self.root

    @classmethod
    def random(cls, n_notes: int | None = None, octaves: tuple[int, ...] = (3, 4, 5)) -> SpecificChord:
        if n_notes is None:
            n_notes = random.randint(2, 5)
        notes_space = tuple(
            SpecificNote(note, octave)
            for note, octave in itertools.product(config.chromatic_notes, octaves)
        )
        notes = frozenset(random.sample(notes_space, n_notes))
        return cls(notes)

    @classmethod
    def from_str(cls, string: str) -> SpecificChord:
        notes_, _, root_ = string.partition('/')
        root = Note(root_) if root_ else None
        notes_2 = notes_.split('_')
        if len(notes_2) != len(set(notes_2)):
            raise NotImplementedError('SpecificChord_s with non unique notes are not supported')
        notes = frozenset(SpecificNote.from_str(note) for note in notes_2)
        return cls(notes, root=root)

    def notes_combinations(self) -> Iterator[tuple[SpecificNote, SpecificNote]]:
        yield from itertools.combinations(self.notes_ascending, 2)

    def find_intervals(self, interval: int) -> tuple[tuple[SpecificNote, SpecificNote], ...]:
        return tuple((n, m) for n, m in self.notes_combinations() if abs(m - n) == interval)

    def __len__(self) -> int:
        return len(self.notes)

    def __getitem__(self, item: int) -> SpecificNote:
        return self.notes_ascending[item]

    def __iter__(self) -> Iterator[SpecificNote]:
        return iter(self.notes_ascending)

    def __repr__(self) -> str:
        x = '_'.join(repr(note) for note in self.notes_ascending)
        if self.root is not None:
            return f'{x}/{self.root.name}'
        return x

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SpecificChord):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __sub__(self, other: SpecificChord) -> int:
        return sum(abs(a - b) for a, b in zip(self, other, strict=True))

    def __add__(self, other: int) -> SpecificChord:
        """transpose"""
        if not isinstance(other, int):
            raise TypeError('only adding integers is allowed (transposition)')
        root = self.root + other if self.root is not None else None
        return SpecificChord(frozenset(note + other for note in self), root=root)

    @functools.cached_property
    def transposed_to_C0(self) -> SpecificChord:
        return self + (SpecificNote('C', 0) - self[0])

    def to_piano_image(self) -> str:
        from musictool.noterange import NoteRange
        from musictool.piano import Piano
        noterange = NoteRange(self[0], self[-1]) if self.notes else None
        return Piano(
            note_colors=dict.fromkeys(self.notes, config.RED),
            squares={note: {'text': str(note), 'text_size': '8'} for note in self},
            noterange=noterange,
        )._repr_svg_()

    def _repr_html_(
        self,
        html_classes: tuple[str, ...] = ('card',),
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

    def __getnewargs_ex__(self) -> tuple[tuple[frozenset[SpecificNote]], dict[str, Note | None]]:
        return (self.notes,), {'root': self.root}

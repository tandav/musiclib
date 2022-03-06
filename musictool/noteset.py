from __future__ import annotations

import itertools
import random

import pipe21 as P

from musictool import chromatic
from musictool import config
from musictool.note import AnyNote
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.note import str_to_note
from musictool.util.cache import Cached

'''
NoteSet
    NotesWithRoot
        Scale
        Chord
'''


def bits_to_intervals(bits: str) -> frozenset:
    return (
        bits
        | P.Map(int)
        | P.Pipe(enumerate)
        | P.Pipe(lambda it: itertools.islice(it, 1, None))
        | P.FilterValues()
        | P.Keys()
        | P.Pipe(frozenset)
    )


def intervals_to_bits(intervals: frozenset) -> str:
    bits = ['0'] * 12
    bits[0] = '1'
    for i in intervals:
        bits[i] = '1'
    return ''.join(bits)


class NoteSet(Cached):
    intervals_to_name: dict = {}
    name_to_intervals: dict = {}

    def __init__(
        self,
        notes: frozenset[str | Note],
        *,
        root: str | Note | None = None,
    ):
        """
        an unordered set of notes
        root:
            root note is optional
            notes w/o root has no intervals
        """
        if not isinstance(notes, frozenset):
            raise TypeError(f'expected frozenset, got {type(notes)}')

        if len(notes) == 0:
            raise ValueError('notes should be not empty')

        if isinstance(next(iter(notes)), str):
            notes = frozenset(Note(note) for note in notes)

        if isinstance(root, str):
            root = Note(root)

        if root is not None and root not in notes:
            raise KeyError('root should be one of notes')

        self.notes = notes
        self.root = root
        self.key = self.notes, self.root
        self.notes_ascending = chromatic.sort_notes(self.notes, start=self.root)
        self.note_i = {note: i for i, note in enumerate(self.notes_ascending)}

        if root is not None:
            if root not in notes:
                raise ValueError('root note should be one of the chord notes')

            self.intervals = frozenset(note - root for note in notes - {root})
            self.bits = intervals_to_bits(self.intervals)
            self.name = self.__class__.intervals_to_name.get(self.intervals)

    @property
    def rootless(self): return NoteSet(self.notes)

    def transpose_to(self, note: Note) -> NoteSet:
        if self.root is None:
            raise ValueError('noteset should have root to be transposed')
        return NoteSet.from_intervals(note, self.intervals)

    @classmethod
    def from_name(cls, root: str | Note, name: str) -> NoteSet:
        if isinstance(root, str):
            root = Note(root)
        notes = frozenset(root + interval for interval in cls.name_to_intervals[name]) | {root}
        return cls(notes, root=root)

    @classmethod
    def from_intervals(cls, root: str | Note, intervals: frozenset):
        if isinstance(root, str):
            root = Note(root)
        return cls(frozenset(root + interval for interval in intervals) | {root}, root=root)

    @classmethod
    def random(cls, n_notes=None):
        if n_notes is None:
            n_notes = random.randint(2, 5)
        notes = frozenset(random.sample(config.chromatic_notes, n_notes))
        return cls(notes)

    @classmethod
    def from_str(cls, string: str):
        notes, _, root = string.partition('/')
        root = Note(root) if root else None
        notes = frozenset(Note(note) for note in notes)
        return cls(notes, root=root)

    def add_note(self, note: AnyNote, steps: int) -> Note | SpecificNote:
        notes = self.notes_ascending
        if type(note) is str:
            note = str_to_note(note)
        if type(note) is Note:
            return notes[(notes.index(note) + steps) % len(notes)]
        elif type(note) is SpecificNote:
            # raise NotImplementedError
            octave, i = divmod(notes.index(note.abstract) + steps, len(notes))
            return SpecificNote(notes[i], note.octave + octave)
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
    def __contains__(self, item): return item in self.notes
    def __le__(self, other): return self.notes <= other
    def __ge__(self, other): return other <= self.notes

    # def to_piano_image(self, base64=False):
    #     return Piano(chord=self)._repr_svg_()

    def __repr__(self):
        _ = ''.join(note.name for note in self)
        if self.root is not None:
            _ += f'/{self.root.name}'
        return _

    # async def play(self, seconds=1):
    #     await SpecificChord(
    #         notes=frozenset(SpecificNote(note) for note in self.notes),
    #         root=self.root,
    #     ).play(seconds)
    #     notes_to_play = self.specific_notes
    #
    #     if bass:
    #         notes_to_play = itertools.chain(notes_to_play, [Note(self.root.name, octave=self.root.octave + bass)])
    #
    #     tasks = tuple(note.play(seconds) for note in notes_to_play)
    #     await asyncio.gather(*tasks)

    # def _repr_html_(self):
    #     label = hasattr(self, 'label') and f"id={self.label!r}"or ''
    #     number = hasattr(self, 'number') and self.number or ''
    #
    #     return f'''
    #     <li class='card {self.name}' {label}>
    #     <a href='play_chord_{self.str_chord}'>
    #     <span class='card_header' ><h3>{number} {self.root} {self.name}</h3></span>
    #     <img src='{self.to_piano_image(base64=True)}' />
    #     </a>
    #     </li>
    #     '''

    # def __repr__(self):
    #     label = hasattr(self, 'label') and f"id={self.label!r}"or ''
    #     number = hasattr(self, 'number') and self.number or ''
    #
    #     return f'''
    #     <li class='card {self.name}' {label} onclick=play_chord('{str(self)}')>
    #     <span class='card_header' ><h3>{number} {self.root} {self.name}</h3></span>
    #     <img src='{self.to_piano_image(base64=True)}' />
    #     </li>
    #     '''

# class SpecificNotes: pass


class NoteRange:
    def __init__(
        self,
        start: SpecificNote,
        stop: SpecificNote,
        noteset: NoteSet = NoteSet(frozenset(config.chromatic_notes)),
    ):
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
        if 0 <= item < len(self): return self.noteset.add_note(self.start, item)
        elif -len(self) <= item < 0: return self.noteset.add_note(self.stop, item + 1)
        else: raise IndexError('index out of range')

    def __getitem__(self, item: int | slice) -> SpecificNote | NoteRange:
        if isinstance(item, int): return self._getitem_int(item)
        elif isinstance(item, slice):
            if not 0 <= item.start <= item.stop <= len(self):
                raise IndexError('NoteRange slice is out of range')
            return NoteRange(self._getitem_int(item.start), self._getitem_int(item.stop), self.noteset)
        else: raise TypeError('NoteRange indices must be integers or slices, not str')

    def __contains__(self, item: SpecificNote): return item.abstract in self.noteset and self.start <= item <= self.stop
    def __repr__(self): return f'NoteRange({self.start}, {self.stop}, noteset={self.noteset})'
    def __len__(self): return self.noteset.subtract(self.stop, self.start) + 1
    def __eq__(self, other): return self._key == other._key
    def __hash__(self): return hash(self._key)

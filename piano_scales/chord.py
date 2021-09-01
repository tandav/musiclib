import functools
import itertools
from . import config
from .piano import Piano
import asyncio
from collections.abc import Sequence
from typing import Optional
from . import config, util
from .note import Note, SpecificNote
from numbers import Number


class Chord:
    def __init__(
        self,
        notes: frozenset[Note],
        root: Optional[Note] = None,
    ):
        """
        chord is an unordered set of notes
        root:
            root note of a chord (to distinguish between inversions_
            root note is optional, some chord can has no root
            chord w/o root has no intervals
        """

        self.notes = notes
        self.root = root
        self.key = self.notes, self.root
        # self.str_chord = ''.join(note.name for note in self.notes)
        # self.intervals = tuple(n - self.specific_notes[0] for n in self.specific_notes[1:])
        # self.name = {(3, 7): 'minor', (4, 7): 'major', (3, 6): 'diminished'}.get(self.intervals)
        # self.root = str_chord[0]
        # self.root_octave = root_octave
        # self.notes = tuple(Note(note, root_octave) for note in self.str_chord)
        # self.add_notes_no_inverse()

    @classmethod
    def from_intervals(cls, root: Note, intervals: frozenset):
        """
        if you're creating chord from interval, you must specify root note
        from which intervals are calculated
        """
        # instance = cls()
        # instance.intervals
        # instanse.name = {(3, 7): 'minor', (4, 7): 'major', (3, 6): 'diminished'}.get(self.intervals)
        # # name: Optional[str] = None,

        raise NotImplementedError


    def inversions(self):
        raise NotImplementedError

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)
    def __getitem__(self, item): return self.notes[item]
    def __len__(self): return len(self.notes)
    def __contains__(self, item): return item in self.notes
    def __str__(self): return ''.join(note.name for note in self.notes)

    def to_piano_image(self, base64=False):
        return Piano(chord=self)._repr_svg_()
        # return chord_to_piano(self, as_base64=base64)

    def __repr__(self):
        _ = '{' + ' '.join(f'{note.name}' for note in self.notes) + '}'
        return f"Chord({_} / {self.root.name if self.root is not None else self.root})"

    async def play(self, seconds=1):
        await SpecificChord(
            notes = frozenset(SpecificNote(note) for note in self.notes),
            root = self.root,
        ).play(seconds)
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


class SpecificChord:
    def __init__(
        self,
        notes: frozenset[SpecificNote],
        root: Optional[SpecificNote] = None,
    ):
        self.notes = notes
        self.root = root

    # def add_specific_notes(self):
    #     specific_notes = []
    #     for note in self.notes:
    #         if note.octave is not None:
    #             specific_notes.append(note)
    #         else:
    #             specific_notes.append(Note(note.name, octave=config.default_octave))
    #     self.specific_notes = tuple(specific_notes)

    async def play(self, seconds: Number = 1):
        tasks = (note.play(seconds) for note in self.notes)
        await asyncio.gather(*tasks)

class LabeledChord(Chord):
    pass

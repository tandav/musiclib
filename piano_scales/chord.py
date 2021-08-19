import functools
import itertools
import asyncio
from collections.abc import Sequence
from . import config, util
from .piano import chord_to_piano
from .note import Note
from .player import play

class Chord:
    def __init__(self, notes: tuple[Note], root=None):
        self.notes = notes
        if root is None:
            self.root = notes[0]

        self.key = self.notes, self.root

        # self.str_chord = str_chord
        # self.root = str_chord[0]
        self.add_name()
        # self.root_octave = root_octave
        # self.notes = tuple(Note(note, root_octave) for note in self.str_chord)
        # self.add_notes_no_inverse()

    # def add_notes_no_inverse(self):
    #     it = util.iter_notes_with_octaves(self.root_octave)
    #     it = itertools.dropwhile(lambda kv: kv[0] != self.str_chord[0], it)
    #     it = filter(lambda kv: kv[0] in self.str_chord, it)
    #     it = itertools.islice(it, 3)
    #     self.notes_no_inverse = tuple(Note(note, octave) for note, octave in it)


    async def play(self, seconds=1, bass=None):

        # if inverse:
        #     notes_to_play = self.notes
        #
        # else:
        #     notes_to_play = self.notes_no_inverse

        notes_to_play = self.notes

        if bass:
            notes_to_play = itertools.chain(notes_to_play, [Note(self.root.name, octave=self.root.octave + bass)])

        tasks = [note.play(seconds) for note in notes_to_play]
        await asyncio.gather(*tasks)

        # for note in self.notes:
        #     note.play(seconds)
        # play([note.to_midi() for note in self.notes], seconds)

    def inversions(self):
        raise NotImplementedError

    def add_name(self):
        it = itertools.cycle(config.chromatic_notes)
        it = itertools.dropwhile(lambda x: x != self.notes[0].name, it)
        it = enumerate(it)
        it = filter(lambda kv: Note(kv[1]) in self, it)
        it = itertools.islice(it, 3)
        it = list(it)
        intervals = tuple(k for k, v in it[1:])
        self.name = {(3, 7): 'minor', (4, 7): 'major', (3, 6): 'diminished'}[intervals]

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)
    def __getitem__(self, item): return self.notes[item]
    def __len__(self): return len(self.notes)
    def __contains__(self, item): return item in self.notes
    def __str__(self): return ''.join(note.name for note in self.notes)

    def to_piano_image(self, base64=False):
        return chord_to_piano(self, as_base64=base64)

    # def _repr_html_(self):
    # def __repr__(self):
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

    def __repr__(self):
        label = hasattr(self, 'label') and f"id={self.label!r}"or ''
        number = hasattr(self, 'number') and self.number or ''

        return f'''
        <li class='card {self.name}' {label} onclick=play_chord('{str(self)}')>
        <span class='card_header' ><h3>{number} {self.root} {self.name}</h3></span>
        <img src='{self.to_piano_image(base64=True)}' />
        </li>
        '''


class LabeledChord(Chord):
    pass

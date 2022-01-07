import asyncio
import itertools
import random
from numbers import Number

from musictool import config
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noteset import NoteSet


class Chord(NoteSet):
    intervals_to_name = {
        # triads
        frozenset({4, 7}): 'major',
        frozenset({3, 7}): 'minor',
        frozenset({3, 6}): 'diminished',
        # 7th
        frozenset({4, 7, 11}): 'maj7',
        frozenset({4, 7, 10}): '7',
        frozenset({3, 7, 10}): 'min7',
        frozenset({3, 6, 10}): 'half-dim-7',
        frozenset({3, 6, 9}): 'dim-7',
        # 6th
        frozenset({4, 7, 9}): '6',
        frozenset({3, 7, 9}): 'm6',
        # etc
        frozenset({4, 8}): 'aug',
        frozenset({2, 7}): 'sus2',
        frozenset({5, 7}): 'sus4',

    }
    name_to_intervals = {v: k for k, v in intervals_to_name.items()}


class SpecificChord:
    def __init__(
        self,
        notes: frozenset[SpecificNote],
        root: Note | None = None,
    ):
        self.notes = notes
        self.root = root
        self.abstract = Chord(frozenset(note.abstract for note in notes), root)
        self.root_specific = frozenset(note for note in notes if note.abstract == root)

        self.notes_ascending = tuple(sorted(notes, key=lambda note: note.absolute_i))
        self.intervals = tuple(note - self.notes_ascending[0] for note in self.notes_ascending[1:])  # from lowest note
        self.key = self.notes, self.root
        self.str_chord = '_'.join(repr(note) for note in self.notes_ascending)

    @classmethod
    def random(cls, n_notes=None, octaves=None):
        if n_notes is None:
            n_notes = random.randint(2, 5)
        if octaves is None:
            octaves = 3, 4, 5
        notes_space = tuple(
            SpecificNote(note, octave)
            for note, octave in itertools.product(config.chromatic_notes, octaves)
        )
        notes = frozenset(random.sample(notes_space, n_notes))
        return cls(notes)

    @classmethod
    def from_str(cls, string: str):
        notes, _, root = string.partition('/')
        root = Note(root) if root else None
        notes = frozenset(SpecificNote.from_str(note) for note in notes.split('_'))
        return cls(notes, root)

    def notes_combinations(self, ids=False):
        if ids: yield from itertools.combinations(range(len(self.notes_ascending)), 2)
        else: yield from itertools.combinations(self.notes_ascending, 2)
        # for n, m in itertools.combinations(self.notes_ascending, 2):
        #     yield n, m

    def find_intervals(self, interval: int):
        return tuple((n, m) for n, m in self.notes_combinations() if abs(m - n) == interval)

    # def add_note(self, note: Note | SpecificNote, steps: int):
    #     notes = self.notes_ascending
    #     if type(note) is Note:
    #         return notes[(notes.index(note) + steps) % len(notes)]
    #     else:
    #         raise TypeError

    def __repr__(self):
        _ = self.str_chord
        if self.root is not None:
            _ = f'{_}/{self.root.name}'
        return _

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)

    # def __sub__(self, other):
    #     """
    #     https://music.stackexchange.com/a/77630
    #     considering no voice crossing
    #     """
    #     return sum(note.absolute_i for note in self.notes) - sum(note.absolute_i for note in other.notes)

    def __sub__(left, right):
        return sum(abs(l.absolute_i - r.absolute_i) for l, r in zip(left.notes_ascending, right.notes_ascending))

    async def play(self, seconds: Number = 1, bass_octave: int | None = None) -> None:
        tasks = [note.play(seconds) for note in self.notes]
        if bass_octave:
            if self.root is None:
                raise ValueError('cannot play bass when root is None')
            tasks.append(SpecificNote(self.root, bass_octave).play(seconds))
        await asyncio.gather(*tasks)

    def to_midi(self, path=None, n_bars=1):
        import mido
        mid = mido.MidiFile(type=0, ticks_per_beat=96)
        track = mido.MidiTrack()
        track.append(mido.MetaMessage(type='track_name', name='test_name'))
        track.append(mido.MetaMessage(type='time_signature', numerator=4, denominator=4, clocks_per_click=36))
        track.append(mido.MetaMessage(type='time_signature', numerator=4, denominator=4, clocks_per_click=36))
        if self.root is not None:
            track.append(mido.MetaMessage(type='marker', text=self.root.name))

        stop_time = int(n_bars * mid.ticks_per_beat * 4)

        for note in self.notes_ascending:
            track.append(mido.Message('note_on', note=note.absolute_i, velocity=100, time=0))
        for i, note in enumerate(self.notes_ascending):
            track.append(mido.Message('note_off', note=note.absolute_i, velocity=100, time=stop_time if i == 0 else 0))

        mid.tracks.append(track)
        mid.meta = {'chord': self}
        if path is None:
            return mid
        mid.save(path)

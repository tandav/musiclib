import functools
import itertools
import random
import statistics
from collections import deque

import mido
import pipe21 as P

from musictool import config
from musictool.util.iteration import sequence_builder


class Rhythm:
    def __init__(
        self,
        notes: tuple,
        beats_per_minute: int = config.beats_per_minute,
        beats_per_bar: int = 4,
        bar_notes: int = 16,  # kinda grid size
    ):
        self.notes = notes
        self.beats_per_minute = beats_per_minute
        self.beats_per_second = beats_per_minute / 60
        self.beats_per_bar = beats_per_bar
        self.bar_seconds = beats_per_bar / self.beats_per_second
        self.bar_notes = bar_notes
        self.note_seconds = self.bar_seconds / bar_notes
        self.bits = ''.join(map(str, self.notes))

    @classmethod
    def random_rhythm(cls, n_notes: int | None = None, bar_notes: int = 16):
        if not (0 < n_notes <= bar_notes):
            raise ValueError(f'number of notes should be more than 1 and less than bar_notes={bar_notes}')
        if n_notes is None:
            n_notes = random.randint(1, bar_notes)
        notes = [1] * n_notes + [0] * (bar_notes - n_notes)
        random.shuffle(notes)
        notes = tuple(notes)
        return cls(notes, bar_notes=bar_notes)

    def __repr__(self):
        return f"Rhythm('{self.bits}')"

    @functools.cached_property
    def has_contiguous_ones(self):
        return (
            self.notes[0] == 1 and self.notes[-1] == 1
            or any(len(list(g)) > 1 for k, g in itertools.groupby(self.notes, key=bool) if k)
        )

    @staticmethod
    def no_contiguous_ones(prev, curr):
        return not (prev == curr == 1)

    @functools.cached_property
    def score(self) -> float:
        """spacings variance"""
        x = self.notes
        if x[0] != 1:  # rotate until first element == 1
            x = deque(x)
            x.rotate(-x.index(1))
        spacings = [len(list(g)) for k, g in itertools.groupby(x, key=bool) if not k]
        if len(spacings) == 1:  # TODO: try normalize into 0..1
            return float('inf')
        return statistics.variance(spacings)

    @staticmethod
    def all_rhythms(n_notes: int | None = None, bar_notes: int = 16, sort_by_score=False):
        rhythms = sequence_builder(
            n=bar_notes,
            options=(0, 1),
            curr_prev_constraint=Rhythm.no_contiguous_ones,
        )

        if n_notes is not None:
            rhythms = rhythms | P.Filter(lambda r: sum(r) == n_notes)

        rhythms = (Rhythm(r, bar_notes=bar_notes) for r in rhythms)

        if sort_by_score:
            rhythms = (
                rhythms
                | P.KeyBy(lambda rhythm: rhythm.score)
                | P.Pipe(lambda x: sorted(x, key=lambda score_rhythm: (score_rhythm[0], score_rhythm[1].notes)))
            )
        return rhythms | P.Pipe(tuple)

    def play(self):
        raise NotImplementedError

    def to_midi(self, path=None, note_=None, chord=None, progression=None) -> 'mido.MidiFile | None':

        mid = mido.MidiFile(type=0, ticks_per_beat=96)

        ticks_per_note = mid.ticks_per_beat * self.beats_per_bar // self.bar_notes
        track = mido.MidiTrack()
        track.append(mido.MetaMessage(type='track_name', name='test_name'))
        track.append(mido.MetaMessage(type='time_signature', numerator=4, denominator=4, clocks_per_click=36))
        t = 0

        def append_bar(chord):
            nonlocal t
            for is_play in self.notes:
                if is_play:
                    notes = [note_.absolute_i] if chord is None else [note.absolute_i for note in chord.notes]
                    for i, note in enumerate(notes):
                        track.append(mido.Message('note_on', note=note, velocity=100, time=t if i == 0 else 0))
                    for i, note in enumerate(notes):
                        track.append(mido.Message('note_off', note=note, velocity=100, time=ticks_per_note if i == 0 else 0))
                    t = 0
                else:
                    t += ticks_per_note

        if progression is None:
            append_bar(chord)
        else:
            for chord in progression:
                append_bar(chord)

        mid.tracks.append(track)
        if path is None:
            return mid
        mid.save(path)

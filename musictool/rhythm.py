from __future__ import annotations

import functools
import itertools
import random
import statistics
from collections.abc import Iterable
from pathlib import Path

import mido
import pipe21 as P

from musictool import config
from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.util.cache import Cached
from musictool.util.sequence_builder import SequenceBuilder

TO_MIDI_MUTUAL_EXCLUSIVE_ERROR = TypeError('options, options_i, options_callable are mutually exclusive. Only 1 must be not None')


class Rhythm(Cached):
    def __init__(
        self,
        notes: tuple[int, ...],
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
    def random_rhythm(cls, n_notes: int | None = None, bar_notes: int = 16) -> Rhythm:
        if n_notes is None:
            n_notes = random.randint(1, bar_notes)
        if not (0 < n_notes <= bar_notes):
            raise ValueError(f'number of notes should be more than 1 and less than bar_notes={bar_notes}')
        notes = [1] * n_notes + [0] * (bar_notes - n_notes)
        random.shuffle(notes)
        return cls(tuple(notes), bar_notes=bar_notes)

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
        first_1 = self.notes.index(1)
        x = self.notes[first_1:] + self.notes[:first_1]
        spacings = [len(list(g)) for k, g in itertools.groupby(x, key=bool) if not k]
        if len(spacings) == 1:  # TODO: try normalize into 0..1
            return float('inf')
        return statistics.variance(spacings)

    @staticmethod
    def all_rhythms(n_notes: int | None = None, bar_notes: int = 16, sort_by_score: bool = False) -> tuple[Rhythm, ...]:
        rhythms_ = SequenceBuilder(
            n=bar_notes,
            options=(0, 1),
            curr_prev_constraint={-1: Rhythm.no_contiguous_ones},
        )

        if n_notes is not None:
            rhythms_ = rhythms_ | P.Filter(lambda r: sum(r) == n_notes)

        rhythms = (Rhythm(r, bar_notes=bar_notes) for r in rhythms_)

        if sort_by_score:
            rhythms = (
                rhythms
                | P.KeyBy(lambda rhythm: rhythm.score)
                | P.Pipe(lambda x: sorted(x, key=lambda score_rhythm: (score_rhythm[0], score_rhythm[1].notes)))
            )
        out: tuple[Rhythm] = rhythms | P.Pipe(tuple)
        return out

    def play(self):
        raise NotImplementedError

    def to_midi(
        self,
        path: str | Path | None = None,
        note_: SpecificNote | None = None,
        chord: SpecificChord | None = None,
        progression: Iterable[SpecificChord] | None = None,
    ) -> mido.MidiFile | None:

        if note_ is not None and chord is not None:
            raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR

        if chord is None:
            if note_ is None:
                raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR
            note__ = note_

        if note_ is None:
            if chord is None:
                raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR

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
                    notes = [note__.i] if chord is None else [note.i for note in chord.notes]
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
        return None

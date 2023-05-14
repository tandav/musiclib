from __future__ import annotations

import functools
import itertools
import random
import statistics

import pipe21 as P  # noqa: N812

from musiclib import config
from musiclib.util.cache import Cached
from musiclib.util.sequence_builder import SequenceBuilder


class Rhythm(Cached):
    def __init__(
        self,
        notes: tuple[int, ...],
        beats_per_minute: int = config.beats_per_minute,
        beats_per_bar: int = 4,
        bar_notes: int = 16,  # kinda grid size
    ) -> None:
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
        if not 0 < n_notes <= bar_notes:
            raise ValueError(f'number of notes should be more than 1 and less than bar_notes={bar_notes}')
        notes = [1] * n_notes + [0] * (bar_notes - n_notes)
        random.shuffle(notes)
        return cls(tuple(notes), bar_notes=bar_notes)

    def __repr__(self) -> str:
        return f"Rhythm('{self.bits}')"

    @functools.cached_property
    def has_contiguous_ones(self) -> bool:
        return (
            self.notes[0] == 1 and self.notes[-1] == 1
            or any(len(list(g)) > 1 for k, g in itertools.groupby(self.notes, key=bool) if k)
        )

    @staticmethod
    def have_no_contiguous_ones(prev: int, curr: int) -> bool:
        return not prev == curr == 1

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
    def all_rhythms(*, n_notes: int | None = None, bar_notes: int = 16, sort_by_score: bool = False) -> tuple[Rhythm, ...]:
        rhythms__ = SequenceBuilder(
            n=bar_notes,
            options=(0, 1),
            curr_prev_constraint={-1: Rhythm.have_no_contiguous_ones},
        )

        if n_notes is not None:
            rhythms_ = rhythms__ | P.Filter(lambda r: sum(r) == n_notes)

        rhythms = (Rhythm(r, bar_notes=bar_notes) for r in rhythms_)

        if sort_by_score:
            rhythms = (
                rhythms
                | P.KeyBy(lambda rhythm: rhythm.score)
                | P.Pipe(lambda x: sorted(x, key=lambda score_rhythm: (score_rhythm[0], score_rhythm[1].notes)))
            )
        out: tuple[Rhythm] = rhythms | P.Pipe(tuple)
        return out

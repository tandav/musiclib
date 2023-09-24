from __future__ import annotations

import typing as tp

import mido

DEFAULT_TICKS_PER_BEAT = 96
DEFAULT_BEATS_PER_BAR = 4
DEFAULT_BEATS_PER_MINUTE = 120


class Tempo:
    def __init__(
        self,
        ticks: int = 0,
        ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT,
        beats_per_bar: int = DEFAULT_BEATS_PER_BAR,
        beats_per_minute: float = DEFAULT_BEATS_PER_MINUTE,
    ) -> None:
        self.ticks = ticks
        self.ticks_per_beat = ticks_per_beat
        self.beats_per_bar = beats_per_bar
        self.beats_per_minute = beats_per_minute

    @classmethod
    def from_beats(
        cls,
        beats: float,
        ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT,
        **kwargs: tp.Any,
    ) -> Tempo:
        return cls(
            ticks=int(beats * ticks_per_beat),
            ticks_per_beat=ticks_per_beat,
            **kwargs,
        )

    @classmethod
    def from_bars(
        cls,
        bars: float,
        ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT,
        beats_per_bar: int = DEFAULT_BEATS_PER_BAR,
        **kwargs: tp.Any,
    ) -> Tempo:
        return cls(
            ticks=int(bars * beats_per_bar * ticks_per_beat),
            ticks_per_beat=ticks_per_beat,
            beats_per_bar=beats_per_bar,
            **kwargs,
        )

    @classmethod
    def from_seconds(
        cls,
        seconds: float,
        ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT,
        beats_per_minute: float = DEFAULT_BEATS_PER_MINUTE,
        **kwargs: tp.Any,
    ) -> Tempo:
        return cls(
            ticks=int(seconds * beats_per_minute / 60 * ticks_per_beat),
            ticks_per_beat=ticks_per_beat,
            beats_per_minute=beats_per_minute,
            **kwargs,
        )

    @property
    def beats(self) -> float:
        return self.ticks / self.ticks_per_beat

    @property
    def bars(self) -> float:
        return self.beats / self.beats_per_bar

    @property
    def seconds(self) -> float:
        return self.beats / self.beats_per_minute * 60

    @property
    def beats_per_second(self) -> float:
        return self.beats_per_minute / 60

    @property
    def ticks_per_second(self) -> float:
        return self.ticks_per_beat * self.beats_per_second

    @property
    def bars_per_second(self) -> float:
        return self.beats_per_second / self.beats_per_bar

    @property
    def ticks_per_bar(self) -> int:
        return self.ticks_per_beat * self.beats_per_bar

    @property
    def midi_tempo(self) -> int:
        return mido.bpm2tempo(bpm=self.beats_per_minute, time_signature=(self.beats_per_bar, 4))  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        return f'Tempo(ticks={self.ticks!r}, ticks_per_beat={self.ticks_per_beat!r}, beats_per_bar={self.beats_per_bar!r}, beats_per_minute={self.beats_per_minute!r})'

import typing as tp

import pytest
from musiclib.tempo import Tempo


class Config(tp.NamedTuple):
    ticks: int = 96 * 4
    ticks_per_beat: int = 96
    beats_per_bar: int = 4
    beats_per_minute: float = 120
    beats: float = 4
    bars: float = 1
    seconds: float = 2
    beats_per_second: float = 2
    ticks_per_second: float = 96 * 2
    bars_per_second: float = 0.5
    ticks_per_bar: int = 96 * 4
    midi_tempo: int = 500000


config = Config()


@pytest.fixture(
    params=[
        Tempo(
            ticks=config.ticks,
            ticks_per_beat=config.ticks_per_beat,
            beats_per_bar=config.beats_per_bar,
            beats_per_minute=config.beats_per_minute,
        ),
        Tempo.from_beats(
            beats=config.beats,
            ticks_per_beat=config.ticks_per_beat,
            beats_per_bar=config.beats_per_bar,
            beats_per_minute=config.beats_per_minute,
        ),
        Tempo.from_bars(
            bars=config.bars,
            ticks_per_beat=config.ticks_per_beat,
            beats_per_bar=config.beats_per_bar,
            beats_per_minute=config.beats_per_minute,
        ),
        Tempo.from_seconds(
            seconds=config.seconds,
            ticks_per_beat=config.ticks_per_beat,
            beats_per_bar=config.beats_per_bar,
            beats_per_minute=config.beats_per_minute,
        ),
    ],
)
def tempo(request):
    return request.param


def test_units(tempo):
    for k, v in config._asdict().items():
        assert getattr(tempo, k) == v


@pytest.mark.parametrize(
    ('x', 's', 'r'), [
        (
            Tempo(),
            'Tempo(ticks=0, ticks_per_beat=96, beats_per_bar=4, beats_per_minute=120)',
            'Tempo(ticks=0, ticks_per_beat=96, beats_per_bar=4, beats_per_minute=120)',
        ),
    ],
)
def test_str_repr(x, s, r):
    assert str(x) == s
    assert repr(x) == r

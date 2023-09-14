def bars_to_seconds(
    bars: float,
    bpm: float = 120,
    beats_per_bar: int = 4,
) -> float:
    return bars * 60 * beats_per_bar / bpm


def ticks_to_seconds(ticks: int, ticks_per_beat: int = 96, bpm: float = 120) -> float:
    return ticks / (ticks_per_beat * bpm / 60)


def bars_to_ticks(bars: float, ticks_per_beat: int = 96, beats_per_bar: int = 4) -> int:
    return int(bars * ticks_per_beat * beats_per_bar)


def ticks_to_bars(ticks: int, ticks_per_beat: int = 96, beats_per_bar: int = 4) -> float:
    return ticks / (ticks_per_beat * beats_per_bar)

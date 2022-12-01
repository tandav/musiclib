from musiclib import config


def bars_to_seconds(
    bars: int | float,
    bpm: int | float = config.beats_per_minute,
    beats_per_bar: int = config.beats_per_bar,
) -> float:
    return bars * 60 * beats_per_bar / bpm

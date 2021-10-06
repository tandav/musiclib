import random
from typing import Optional

bpm = 120  # beats per minute
bps = bpm / 60  # beats per second
bpb = 4  # beats per bar
bar_seconds = bpb / bps
bar_notes = 16  # kinda grid size
note_seconds = bar_seconds / bar_notes


def random_rhythm(n_notes: Optional[int] = None):
    if not (0 < n_notes <= bar_notes):
        raise ValueError('')
    if n_notes is None:
        n_notes = random.randint(1, bar_notes)
    r = [1] * n_notes + [0] * (bar_notes - n_notes)
    random.shuffle(r)
    return r

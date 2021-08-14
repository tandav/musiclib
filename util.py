import functools
import itertools
from collections.abc import Iterable
import config


@functools.lru_cache(1024)
def sort_notes(notes: Iterable):
    return ''.join(sorted(notes, key=config.chromatic_notes.find))


def hex_to_rgb(color):
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def iter_diatonic(start=None, take_n=None):
    it = itertools.cycle(config.name_2_bits)
    if start:
        it = itertools.dropwhile(lambda x: x != start, it)
    if take_n:
        it = itertools.islice(it, take_n)
    return it

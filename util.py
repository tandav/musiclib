import functools
import itertools
from collections.abc import Iterable
import config


@functools.lru_cache(1024)
def sort_notes(notes: Iterable):
    return ''.join(sorted(notes, key=config.chromatic_notes.find))


def hex_to_rgb(color):
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def iter_scales(kind, start=None):
    scales = getattr(config, kind)
    it = itertools.cycle(scales)
    if start:
        it = itertools.dropwhile(lambda x: x != start, it)
    it = itertools.islice(it, len(scales))
    return list(it)

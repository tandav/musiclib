import functools
from collections.abc import Iterable
import config


@functools.lru_cache(1024)
def sort_notes(notes: Iterable):
    return ''.join(sorted(notes, key=config.chromatic_notes.find))

from collections.abc import Iterable

from musictool import config
from musictool.note import AnyNote
from musictool.note import Note
from musictool.note import SpecificNote


def sort_notes(it: Iterable[AnyNote], start: AnyNote | None = None) -> tuple:
    first = next(iter(it))
    if isinstance(first, str): out = sorted(it, key=config.note_i.__getitem__)
    elif type(first) is Note: out = sorted(it, key=lambda note: note.i)
    elif type(first) is SpecificNote: out = sorted(it, key=lambda note: note.absolute_i)
    else: raise TypeError

    out = tuple(out)

    if start is None:
        return out

    i = out.index(start)
    return out[i:] + out[:i]

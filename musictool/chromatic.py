import itertools
from collections.abc import Iterable

from musictool import config
from musictool.note import AnyNote
from musictool.note import Note
from musictool.note import SpecificNote


def iterate(
    start_note: AnyNote = config.chromatic_notes[0],
    take_n: int | None = None,
) -> Iterable[Note | SpecificNote]:
    names = itertools.cycle(config.chromatic_notes)

    if isinstance(start_note, SpecificNote):
        octaves = itertools.chain.from_iterable(
            itertools.repeat(octave, 12)
            for octave in itertools.count(start=start_note.octave)
        )
        notes = (SpecificNote(name, octave) for name, octave in zip(names, octaves))
    else:
        if isinstance(start_note, str):
            start_note = Note(start_note)
        notes = (Note(name) for name in names)

    notes = itertools.dropwhile(lambda note: note.name != start_note.name, notes)

    if take_n is not None:
        notes = itertools.islice(notes, take_n)

    yield from notes


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

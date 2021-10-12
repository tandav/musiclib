import asyncio
import functools
import numpy as np
from numbers import Number
from typing import Union  # TODO: python3.10 just use X | Y

from . import config
from . import midi


class Note:  # Note(str) ??
    """
    abstract note, no octave/key
    kinda music theoretic pitch-class
    """
    def __init__(self, name: str):
        """:param name: one of CdDeEFfGaAbB"""
        self.name = name
        self.i = config.note_i[name]

    @classmethod
    def from_i(cls, i):
        return cls(config.chromatic_notes[i])

    async def play(self, seconds: Number = 1):
        await SpecificNote(self).play(seconds)

    def short_repr(self): return self.name
    def __repr__(self): return f"Note(name={self.name})"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Note):
            return self.name == other.name

    def __hash__(self): return hash(self.name)

    def __sub__(self, other):
        """
        kinda constraint (may be it will be changed later):
            if you computing distance between abstract notes - then self considered above other
            G - C == 7 # C0 G0
            C - G == 5 # G0 C1
        """
        if other.i <= self.i:
            return self.i - other.i
        return 12 + self.i - other.i


@functools.total_ordering
class SpecificNote(Note):
    def __init__(self, abstract: Union[Note, str], octave: int = config.default_octave):
        """
        :param octave: in midi format (C5-midi == C3-ableton)
        """
        if isinstance(abstract, str):
            abstract = Note(abstract)
        self.abstract = abstract
        super().__init__(abstract.name)
        self.octave = octave
        self.absolute_i = octave * 12 + self.i  # this is also midi_code
        self.key = self.abstract, self.octave

    @classmethod
    def from_absolute_i(cls, absolute_i: int):
        div, mod = divmod(absolute_i, 12)
        return cls(Note(config.chromatic_notes[mod]), octave=div)

    async def play(self, seconds: Number = 1):
        midi.send_message('note_on', note=self.absolute_i, channel=0)
        await asyncio.sleep(seconds)
        midi.send_message('note_off', note=self.absolute_i, channel=0)

    def __repr__(self): return f'{self.abstract.name}{self.octave}'
    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)
    def __lt__(self, other): return self.absolute_i < other.absolute_i

    @functools.cache
    def __sub__(self, other):
        """distance between notes"""
        return self.absolute_i - other.absolute_i

    def __add__(self, other: int):
        """C + 7 = G"""
        raise NotImplementedError


def note_range(start: SpecificNote, stop: SpecificNote) -> tuple[SpecificNote]:
    return tuple(SpecificNote.from_absolute_i(i) for i in range(start.absolute_i, stop.absolute_i + 1))



class PlayedNote:
    def __init__(
        self,
        absolute_i: int,
        sample_on: int,
        second_on: float,
        sample_off: int,
        second_off: float,
        vst = None,
    ):
        self.note = SpecificNote.from_absolute_i(absolute_i)
        self.sample_on = sample_on
        self.second_on = second_on
        self.sample_off = sample_off
        self.second_off = second_off
        self.samples_rendered = 0
        self.vst = vst

    def render(self, n_samples):
        f = (440 / 32) * (2 ** ((self.note.absolute_i - 9) / 12))
        t0 = self.samples_rendered / config.sample_rate
        t1 = t0 + n_samples / config.sample_rate
        self.samples_rendered += n_samples
        wave = self.vst(np.linspace(t0, t1, n_samples, endpoint=False), f, a=0.3)
        #wave = sine(np.linspace(t0, t1, n_samples, endpoint=False), f, a=0.3)
        return wave

    def __hash__(self):
        return hash((self.note, self.sample_on, self.sample_off))

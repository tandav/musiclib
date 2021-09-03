import asyncio
from numbers import Number
from typing import Union  # TODO: python3.10 just use X | Y

import mido

from . import config


class Note:
    """
    abstract note, no octave/key not playable
    kinda music theoretic  pitch-class
    """
    def __init__(self, name: str):
        """:param name: one of CdDeEFfGaAbB"""
        self.name = name
        self.i = config.chromatic_notes.index(name)

    async def play(self, seconds: Number = 1):
        await SpecificNote(self).play(seconds)

    def __repr__(self): return f"Note(name={self.name})"
    def __eq__(self, other): return self.name == other.name
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
        self.absolute_i = octave * 12 + self.i # this is also midi_code
        self.key = self.abstract, self.octave



    async def play(self, seconds: Number = 1):
        config.port.send(mido.Message('note_on', note=self.absolute_i, channel=0))
        await asyncio.sleep(seconds)
        config.port.send(mido.Message('note_off', note=self.absolute_i, channel=0))

    def __repr__(self): return f"SpecificNote(name={self.abstract.name}, octave={self.octave})"
    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)

    def __sub__(self, other):
        """distance between notes"""
        return self.absolute_i - self.absolute_i

    def __add__(self, other: int):
        """C + 7 = G"""
        raise NotImplementedError

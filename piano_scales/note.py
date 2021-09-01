import asyncio
import mido
from . import config
import warnings


class Note:
    """
    abstract note, no octave/key not playable
    kinda music theoretic  pitch-class
    """
    def __init__(self, name: str):
        """:param name: one of CdDeEFfGaAbB"""
        self.name = name
        self.i = config.chromatic_notes.index(name)

    def __repr__(self): return f"Note(name={self.name})"
    def __eq__(self, other): return self.name == other.name
    def __hash__(self): return hash(self.name)


class SpecificNote:
    def __init__(self, abstract: Note, octave: int = config.default_octave):
        """
        :param octave: in midi format (C5-midi == C3-ableton)
        """
        self.abstract = abstract
        self.octave = octave
        self.absolute_i = octave * 12 + abstract.i # this is also midi_code
        self.key = self.abstract, self.octave



    async def play(self, seconds=1):
        warnings.warn(f'note_on {self} {seconds=}')
        config.port.send(mido.Message('note_on', note=self.absolute_i, channel=0))
        await asyncio.sleep(seconds)
        warnings.warn(f'note_off {self}')
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

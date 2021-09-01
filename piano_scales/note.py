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
        self.name = name

    def __repr__(self): return f"Note(name={self.name})"
    def __eq__(self, other): return self.name == other.name
    def __hash__(self): return hash(self.name)


class SpecificNote(Note):
    def __init__(self, name: str, octave: int):
        """
        :param name: one of CdDeEFfGaAbB
        :param octave: in midi format (C5-midi == C3-ableton)
        """
        super().__init__(name)
        self.octave = octave
        self.i = config.chromatic_notes.index(name)
        self.key = self.name, self.octave

    def abstract(self):
        return

    async def play(self, seconds=1):
        midi_code = self.octave * 12 + self.i
        warnings.warn(f'note_on {self} {seconds=}')
        config.port.send(mido.Message('note_on', note=midi_code, channel=0))
        await asyncio.sleep(seconds)
        warnings.warn(f'note_off {self}')
        config.port.send(mido.Message('note_off', note=midi_code, channel=0))

    def __repr__(self): return f"Note(name={self.name}, octave={self.octave})"
    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)

    def __sub__(self, other):
        """distance between notes"""
        return (self.octave * 12 + self.i) - (other.octave * 12 + other.i)



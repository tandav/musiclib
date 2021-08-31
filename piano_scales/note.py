import asyncio
import mido
from . import config
import warnings
from typing import Optional


class Note:
    def __init__(self, name: str, octave: Optional[int] = None):
        '''
        :param name: one of CdDeEFfGaAbB
        :param octave: in midi format (C5-midi == C3-ableton)
        '''
        self.name = name
        self.octave = octave
        self.i = config.chromatic_notes.index(name)
        if self.octave is not None:
            self.midi_code = self.octave * 12 + self.i
        self.key = self.name, self.octave

    async def play(self, seconds=1):
        warnings.warn(f'note_on {self} {seconds=}')
        config.port.send(mido.Message('note_on', note=self.midi_code, channel=0))
        await asyncio.sleep(seconds)
        warnings.warn(f'note_off {self}')
        config.port.send(mido.Message('note_off', note=self.midi_code, channel=0))


    def __repr__(self):
        return f"Note(name={self.name}, octave={self.octave}, i={self.i}, midi_code={self.midi_code})"

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)

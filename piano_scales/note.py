import asyncio
import mido
from . import config
import warnings

class Note:
    def __init__(self, name, octave=5):
        '''
        :param name: one of CdDeEFfGaAbB
        :param octave: in midi format (C5 equals C3 in ableton)
        '''
        self.name = name
        self.octave = octave
        self.i = config.chromatic_notes.index(name)
        self.midi_code = self.octave * 12 + self.i

    async def play(self, seconds=1):
        warnings.warn(f'note_on {self} {seconds=}')
        config.port.send(mido.Message('note_on', note=self.midi_code, channel=0))
        await asyncio.sleep(seconds)
        warnings.warn(f'note_off {self}')
        config.port.send(mido.Message('note_off', note=self.midi_code, channel=0))


    def __repr__(self):
        return f"Note(name={self.name}, octave={self.octave}, i={self.i}, modo_code={self.midi_code})"

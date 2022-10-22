import asyncio
import functools

import mido

from musictool.chord import SpecificChord
from musictool.note import SpecificNote

Playable = SpecificNote | SpecificChord


class Player:
    def __init__(self, midi_device: str | None = None) -> None:
        if midi_device is None:
            self.send_message = self._print_message
        else:
            self.port = mido.open_output(midi_device)
            self.send_message = self._send_message

    def _print_message(self, *args: str | int, note: int, **kwargs: str | int) -> None:
        print('MIDI_DEVICE not found |', *args, f'{note=},', ', '.join(f'{k}={v!r}' for k, v in kwargs.items()))

    def _send_message(self, *args: str | int, note: int, **kwargs: str | int) -> None:
        note += 24  # to match ableton octaves
        self.port.send(mido.Message(*args, note=note, **kwargs))

    @functools.singledispatchmethod
    async def play(self, obj: Playable, seconds: float = 1) -> None:
        ...

    @play.register
    async def _(self, obj: SpecificNote, seconds: float = 1) -> None:
        self.send_message('note_on', note=obj.i, channel=0)
        await asyncio.sleep(seconds)
        self.send_message('note_off', note=obj.i, channel=0)

    @play.register
    async def _(self, obj: SpecificChord, seconds: float = 1, bass_octave: int | None = None) -> None:
        tasks = [self.play(note, seconds) for note in obj.notes]
        if bass_octave:
            if obj.root is None:
                raise ValueError('cannot play bass when root is None')
            tasks.append(self.play(SpecificNote(obj.root, bass_octave), seconds))
        await asyncio.gather(*tasks)

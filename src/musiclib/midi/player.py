import asyncio
import functools

import mido
import mido.midifiles.midifiles

from musiclib.note import SpecificNote
from musiclib.noteset import SpecificNoteSet

Playable = SpecificNote | SpecificNoteSet


class Player:
    def __init__(self, midi_device: str | None = None) -> None:
        if midi_device is None:
            self.send_message = self._print_message
        else:
            self.port = mido.open_output(midi_device)
            self.send_message = self._send_message

    def _print_message(self, message: mido.Message) -> None:
        print('MIDI_DEVICE not found |', message)  # noqa: T201

    def _send_message(self, message: mido.Message) -> None:
        self.port.send(message)

    @functools.singledispatchmethod
    async def play(
        self,
        obj: Playable,  # pylint: disable=unused-argument
        seconds: float = 1,  # pylint: disable=unused-argument
        channel: int = 0,  # pylint: disable=unused-argument
        velocity: int = 100,  # pylint: disable=unused-argument
    ) -> None:
        ...

    @play.register
    async def _(
        self,
        obj: SpecificNote,
        seconds: float = 1,
        channel: int = 0,
        velocity: int = 100,
    ) -> None:
        self.send_message(mido.Message(type='note_on', channel=channel, note=obj.i, velocity=velocity))
        await asyncio.sleep(seconds)
        self.send_message(mido.Message(type='note_off', channel=channel, note=obj.i, velocity=velocity))

    @play.register
    async def _(
        self,
        obj: SpecificNoteSet,
        seconds: float = 1,
        channel: int = 0,
        velocity: int = 100,
    ) -> None:
        tasks = [self.play(note, seconds, channel, velocity) for note in obj.notes]
        await asyncio.gather(*tasks)

    def play_midi(self, midi: mido.MidiFile, beats_per_minute: float = 120) -> None:
        default_tempo = mido.midifiles.midifiles.DEFAULT_TEMPO
        mido.midifiles.midifiles.DEFAULT_TEMPO = mido.bpm2tempo(beats_per_minute)
        for message in midi.play():
            self.send_message(message)
        mido.midifiles.midifiles.DEFAULT_TEMPO = default_tempo

    async def aio_play_midi(self, midi: mido.MidiFile, beats_per_minute: float = 120) -> None:
        """For some reason this async method is playing with weird delays and time glitches unlike play_midi()"""
        default_tempo = mido.midifiles.midifiles.DEFAULT_TEMPO
        mido.midifiles.midifiles.DEFAULT_TEMPO = mido.bpm2tempo(beats_per_minute)
        for message in midi:
            self.send_message(message)
            await asyncio.sleep(message.time)
        mido.midifiles.midifiles.DEFAULT_TEMPO = default_tempo

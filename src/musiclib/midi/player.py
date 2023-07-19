import asyncio
import functools
from collections.abc import Iterable
from pathlib import Path

import mido

from musiclib.chord import SpecificChord
from musiclib.note import SpecificNote
from musiclib.rhythm import Rhythm

Playable = SpecificNote | SpecificChord


class Player:
    def __init__(self, midi_device: str | None = None) -> None:
        if midi_device is None:
            self.send_message = self._print_message
        else:
            self.port = mido.open_output(midi_device)
            self.send_message = self._send_message

    def _print_message(self, *args: str | int, note: int, **kwargs: str | int) -> None:
        print('MIDI_DEVICE not found |', *args, f'{note=},', ', '.join(f'{k}={v!r}' for k, v in kwargs.items()))  # noqa: T201

    def _send_message(self, *args: str | int, note: int, **kwargs: str | int) -> None:
        note += 24  # to match ableton octaves
        self.port.send(mido.Message(*args, note=note, **kwargs))

    @functools.singledispatchmethod
    async def play(self, obj: Playable, seconds: float = 1) -> None:  # pylint: disable=unused-argument
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


def chord_to_midi(
    chord: SpecificChord,
    path: str | Path | None = None,
    n_bars: int = 1,
) -> mido.MidiFile | None:
    mid = mido.MidiFile(type=0, ticks_per_beat=96)
    track = mido.MidiTrack()
    track.append(mido.MetaMessage(type='track_name', name='test_name'))
    track.append(mido.MetaMessage(type='time_signature', numerator=4, denominator=4, clocks_per_click=36))
    track.append(mido.MetaMessage(type='time_signature', numerator=4, denominator=4, clocks_per_click=36))
    if chord.root is not None:
        track.append(mido.MetaMessage(type='marker', text=chord.root.name))

    stop_time = int(n_bars * mid.ticks_per_beat * 4)

    for note in chord.notes_ascending:
        track.append(mido.Message('note_on', note=note.i, velocity=100, time=0))  # noqa: PERF401
    for i, note in enumerate(chord.notes_ascending):
        track.append(mido.Message('note_off', note=note.i, velocity=100, time=stop_time if i == 0 else 0))

    mid.tracks.append(track)
    mid.meta = {'chord': chord}
    if path is None:
        return mid
    mid.save(path)
    return None


TO_MIDI_MUTUAL_EXCLUSIVE_ERROR = TypeError('note_, chord are mutually exclusive. Only 1 must be not None')


def rhythm_to_midi(  # noqa: C901
    rhythm: Rhythm,
    path: str | Path | None = None,
    note_: SpecificNote | None = None,
    chord: SpecificChord | None = None,
    progression: Iterable[SpecificChord] | None = None,
) -> mido.MidiFile | None:

    if note_ is not None and chord is not None:
        raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR

    if chord is None:
        if note_ is None:
            raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR
        note__ = note_

    if note_ is None and chord is None:
        raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR

    mid = mido.MidiFile(type=0, ticks_per_beat=96)

    ticks_per_note = mid.ticks_per_beat * rhythm.beats_per_bar // rhythm.bar_notes
    track = mido.MidiTrack()
    track.append(mido.MetaMessage(type='track_name', name='test_name'))
    track.append(mido.MetaMessage(type='time_signature', numerator=4, denominator=4, clocks_per_click=36))
    t = 0

    def append_bar(chord: SpecificChord | None) -> None:
        nonlocal t
        for is_play in rhythm.notes:
            if is_play:
                notes = [note__.i] if chord is None else [note.i for note in chord.notes]
                for i, note in enumerate(notes):
                    track.append(mido.Message('note_on', note=note, velocity=100, time=t if i == 0 else 0))
                for i, note in enumerate(notes):
                    track.append(mido.Message('note_off', note=note, velocity=100, time=ticks_per_note if i == 0 else 0))
                t = 0
            else:
                t += ticks_per_note

    if progression is None:
        append_bar(chord)
    else:
        for _chord in progression:
            append_bar(_chord)

    mid.tracks.append(track)
    if path is None:
        return mid
    mid.save(path)
    return None

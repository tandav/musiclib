import collections
import dataclasses
import functools
from typing import Literal

import mido

from musiclib.note import SpecificNote


@dataclasses.dataclass(frozen=True)
@functools.total_ordering
class MidiNote:
    note: SpecificNote
    on: int
    off: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MidiNote):
            return NotImplemented
        return self.on == other.on

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, MidiNote):
            return NotImplemented
        return self.on < other.on

    def __hash__(self) -> int:
        return hash((self.note, self.on, self.off))


@dataclasses.dataclass(frozen=True)
class MidiPitch:
    time: int
    pitch: int


@dataclasses.dataclass
class Midi:
    notes: list[MidiNote]
    pitchbend: list[MidiPitch]
    ticks_per_beat: int = 96


def is_note(type_: Literal['on', 'off'], message: mido.Message) -> bool:
    """https://stackoverflow.com/a/43322203/4204843"""
    if type_ == 'on':
        return message.type == 'note_on' and message.velocity > 0  # type: ignore[no-any-return]
    if type_ == 'off':
        return message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0)  # type: ignore[no-any-return]
    raise ValueError


def parse_midi(midi: mido.MidiFile) -> Midi:
    if midi.type != 0:
        raise ValueError('only type 0 midi files are supported')
    track, = midi.tracks
    notes: list[MidiNote] = []
    pitchbend = []
    playing_notes = collections.defaultdict(dict)  # type: ignore[var-annotated]
    t = 0
    for message in track:
        t += message.time
        if is_note('on', message):
            playing_notes[message.note].update({'note': SpecificNote.from_i(message.note), 'on': t})
        elif is_note('off', message):
            note = playing_notes[message.note]
            note['off'] = t
            notes.append(MidiNote(**note))
            del playing_notes[message.note]  # TODO: is this del necessary?
        elif message.type == 'pitchwheel':
            pitchbend.append(MidiPitch(time=t, pitch=message.pitch))
    return Midi(notes=notes, pitchbend=pitchbend, ticks_per_beat=midi.ticks_per_beat)

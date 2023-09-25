import collections
import dataclasses
import functools
from collections.abc import Iterable
from typing import Literal

import mido

from musiclib.note import SpecificNote
from musiclib.noteset import SpecificNoteSet
from musiclib.rhythm import Rhythm
from musiclib.tempo import Tempo


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
    notes: list[MidiNote] = dataclasses.field(default_factory=list)
    pitchbend: list[MidiPitch] = dataclasses.field(default_factory=list)
    ticks_per_beat: int = 96


@dataclasses.dataclass
class IndexedMessage:
    message: mido.Message
    index: int


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


def midiobj_to_midifile(midi: Midi) -> mido.MidiFile:
    abs_messages = index_abs_messages(midi)
    t = 0
    messages = []
    for im in abs_messages:
        m = im.message.copy()
        m.time = im.message.time - t
        messages.append(m)
        t = im.message.time
    track = mido.MidiTrack(messages)
    return mido.MidiFile(type=0, tracks=[track], ticks_per_beat=midi.ticks_per_beat)


def index_abs_messages(midi: Midi) -> list[IndexedMessage]:
    """this are messages with absolute time, note real midi messages"""
    abs_messages = []
    for i, note in enumerate(midi.notes):
        abs_messages.append(IndexedMessage(message=mido.Message(type='note_on', time=note.on, note=note.note.i, velocity=100), index=i))
        abs_messages.append(IndexedMessage(message=mido.Message(type='note_off', time=note.off, note=note.note.i, velocity=100), index=i))
    for i, pitch in enumerate(midi.pitchbend):
        abs_messages.append(IndexedMessage(message=mido.Message(type='pitchwheel', time=pitch.time, pitch=pitch.pitch), index=i))
    # Sort by time. If time is equal sort using type priority in following order: note_on, pitchwheel, note_off
    abs_messages.sort(key=lambda m: (m.message.time, {'note_on': 0, 'pitchwheel': 1, 'note_off': 2}[m.message.type]))
    return abs_messages


def specific_note_set_to_midi(
    noteset: SpecificNoteSet,
    path: str | None = None,
    n_bars: int = 1,
) -> mido.MidiFile:
    mid = mido.MidiFile(type=0, ticks_per_beat=96)
    track = mido.MidiTrack()
    stop_time = int(n_bars * mid.ticks_per_beat * 4)
    for note in noteset.notes_ascending:
        track.append(mido.Message('note_on', note=note.i, velocity=100, time=0))
    for i, note in enumerate(noteset.notes_ascending):
        track.append(mido.Message('note_off', note=note.i, velocity=100, time=stop_time if i == 0 else 0))
    mid.tracks.append(track)
    mid.meta = {'noteset': noteset}
    if path is not None:
        mid.save(path)
    return mid


TO_MIDI_MUTUAL_EXCLUSIVE_ERROR = TypeError('note_, chord are mutually exclusive. Only 1 must be not None')


def rhythm_to_midi(  # noqa: C901
    rhythm: Rhythm,
    path: str | None = None,
    note_: SpecificNote | None = None,
    noteset: SpecificNoteSet | None = None,
    progression: Iterable[SpecificNoteSet] | None = None,
) -> mido.MidiFile:

    if note_ is not None and noteset is not None:
        raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR

    if noteset is None:
        if note_ is None:
            raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR
        note__ = note_

    if note_ is None and noteset is None:
        raise TO_MIDI_MUTUAL_EXCLUSIVE_ERROR

    tempo = Tempo()
    mid = mido.MidiFile(type=0, ticks_per_beat=tempo.ticks_per_beat)

    ticks_per_note = tempo.ticks_per_beat * tempo.beats_per_bar // rhythm.bar_notes
    track = mido.MidiTrack()
    t = 0

    def append_bar(noteset: SpecificNoteSet | None) -> None:
        nonlocal t
        for is_play in rhythm.notes:
            if is_play:
                notes = [note__.i] if noteset is None else [note.i for note in noteset.notes]
                for i, note in enumerate(notes):
                    track.append(mido.Message('note_on', note=note, velocity=100, time=t if i == 0 else 0))
                for i, note in enumerate(notes):
                    track.append(mido.Message('note_off', note=note, velocity=100, time=ticks_per_note if i == 0 else 0))
                t = 0
            else:
                t += ticks_per_note

    if progression is None:
        append_bar(noteset)
    else:
        for _noteset in progression:
            append_bar(_noteset)

    mid.tracks.append(track)
    if path is not None:
        mid.save(path)
    return mid

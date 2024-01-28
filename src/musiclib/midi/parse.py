import collections
import dataclasses
from collections.abc import Generator
from collections.abc import Iterable
from typing import Literal

import mido
from mido.midifiles.tracks import MidiTrack
from mido.midifiles.tracks import _to_abstime
from mido.midifiles.tracks import _to_reltime
from mido.midifiles.tracks import fix_end_of_track

from musiclib.note import SpecificNote
from musiclib.noteset import SpecificNoteSet
from musiclib.rhythm import Rhythm
from musiclib.tempo import Tempo


@dataclasses.dataclass(frozen=True, order=True)
class MidiNote:
    on: int
    off: int
    note: SpecificNote
    channel: int = 0
    velocity: int = 100

    def __post_init__(self) -> None:
        if self.off <= self.on:
            raise ValueError('off must be > on')
        if self.channel not in range(16):
            raise ValueError('channel must be in 0..15')
        if self.velocity not in range(128):
            raise ValueError('velocity must be in 0..127')


@dataclasses.dataclass(frozen=True, order=True)
class MidiPitch:
    time: int
    pitch: int


@dataclasses.dataclass
class Midi:
    notes: list[MidiNote] = dataclasses.field(default_factory=list)
    pitchbend: list[MidiPitch] = dataclasses.field(default_factory=list)
    ticks_per_beat: int = 96

    def __len__(self) -> int:
        return max(note.off for note in self.notes)


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
            del playing_notes[message.note]
        elif message.type == 'pitchwheel':
            pitchbend.append(MidiPitch(time=t, pitch=message.pitch))
    return Midi(notes=notes, pitchbend=pitchbend, ticks_per_beat=midi.ticks_per_beat)


def midiobj_to_midifile(midi: Midi) -> mido.MidiFile:
    track = mido.MidiTrack(_to_reltime(abs_messages(midi)))
    return mido.MidiFile(type=0, tracks=[track], ticks_per_beat=midi.ticks_per_beat)


def abs_messages(midi: Midi) -> list[mido.Message]:
    """this are messages with absolute time, note real midi messages"""
    out = []
    for note in midi.notes:
        out.append(mido.Message(type='note_on', time=note.on, note=note.note.i, velocity=note.velocity, channel=note.channel))
        out.append(mido.Message(type='note_off', time=note.off, note=note.note.i, velocity=note.velocity, channel=note.channel))
    for pitch in midi.pitchbend:
        out.append(mido.Message(type='pitchwheel', time=pitch.time, pitch=pitch.pitch))  # noqa: PERF401
    out.sort(key=lambda m: (m.time, {'note_off': 0, 'pitchwheel': 1, 'note_on': 2}[m.type]))
    return out


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


class SpecificNoteSetEvent:
    def __init__(
        self,
        sns: SpecificNoteSet,
        on: int,
        off: int,
    ) -> None:
        self.sns = sns
        self.on = on
        self.off = off

    def __len__(self) -> int:
        return self.off - self.on

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(sns={self.sns}, on={self.on}, off={self.off})'


def unique_notesets(midi: mido.MidiFile, *, drop_zero_duration: bool = True) -> Generator[SpecificNoteSetEvent, None, None]:
    if midi.type != 0:
        raise ValueError('only type 0 midi files are supported')
    track, = midi.tracks
    playing_notes = collections.defaultdict(dict)  # type: ignore[var-annotated]
    t = 0
    t_sns = 0
    for message in track:
        t += message.time
        if message.type not in {'note_on', 'note_off'}:
            continue
        sns = SpecificNoteSet(frozenset(n['note'] for n in playing_notes.values()))
        if not (drop_zero_duration and t - t_sns == 0):
            yield SpecificNoteSetEvent(sns=sns, on=t_sns, off=t)
        t_sns = t
        if is_note('on', message):
            playing_notes[message.note].update({'note': SpecificNote.from_i(message.note), 'on': t})
        elif is_note('off', message):
            note = playing_notes[message.note]
            note['off'] = t
            del playing_notes[message.note]


def to_dict(midi: mido.MidiFile) -> dict:  # type: ignore[type-arg]
    return {
        'type': midi.type,
        'ticks_per_beat': midi.ticks_per_beat,
        'tracks': [[message.dict() | ({'is_meta': True} if message.is_meta else {}) for message in track] for track in midi.tracks],
    }


def from_dict(midi: dict) -> mido.MidiFile:  # type: ignore[type-arg]
    return mido.MidiFile(
        type=midi['type'],
        ticks_per_beat=midi['ticks_per_beat'],
        tracks=[
            mido.MidiTrack(
                (mido.MetaMessage if message.pop('is_meta', False) else mido.Message).from_dict(message)
                for message in track
            )
            for track in midi['tracks']
        ],
    )


def merge_tracks(tracks, skip_checks=False, key=lambda msg: msg.time):  # type: ignore[no-untyped-def] # noqa: ANN001,ANN201,FBT002
    """Returns a MidiTrack object with all messages from all tracks.

    The messages are returned in playback order with delta times
    as if they were all in one track.

    Pass skip_checks=True to skip validation of messages before merging.
    This should ONLY be used when the messages in tracks have already
    been validated by mido.checks.

    # TODO: make MR to mido
    """
    messages = []
    for track in tracks:
        messages.extend(_to_abstime(track, skip_checks=skip_checks))

    messages.sort(key=key)

    return MidiTrack(
        fix_end_of_track(
            _to_reltime(messages, skip_checks=skip_checks),
            skip_checks=skip_checks,
        ),
    )

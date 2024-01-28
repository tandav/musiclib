from __future__ import annotations

import argparse
import collections
import pathlib
from typing import Literal
from typing import TypeAlias

import mido
import yaml
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator

import musiclib
from musiclib.midi.parse import merge_tracks
from musiclib.midi.player import Player
from musiclib.note import SpecificNote


class ArbitraryTypes(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class EventData(BaseModel):
    type: Literal['Bar', 'RootNote', 'RootTranspose', 'SkipStart', 'SkipStop']
    model_config = ConfigDict(extra='allow')


class RootNoteData(EventData):
    root: str


class RootTransposeData(EventData):
    semitones: int


class BarData(EventData):
    voices: dict[str, list[str]]
    beat_multiplier: float = 1


class Bar:
    def __init__(
        self,
        channel_voices: dict[str, list[list[int | str]]],
        n_beats: int,
        beat_multiplier: float,
    ) -> None:
        self.channel_voices = channel_voices
        self.n_beats = n_beats
        self.beat_multiplier = beat_multiplier
        self.channels_sorted = ['bass', *sorted(self.channel_voices.keys() - {'bass'})]  # sorting is necessary because bass must be first

    @classmethod
    def from_yaml_data(cls, data: BarData) -> Bar:
        channel_voices: dict[str, list[list[int | str]]] = {}
        voices_n_beats = set()
        for channel, voices_str in data.voices.items():
            if channel == 'bass' and len(voices_str) != 1:
                raise ValueError('bass must have only 1 voice')
            channel_voices[channel] = []
            for voice_str in voices_str:
                beats: list[int | str] = []
                for beats_str in voice_str.split():
                    if beats_str in {'..', '--'}:
                        beats.append(beats_str)
                    else:
                        beats.append(int(beats_str, base=12))
                voices_n_beats.add(len(beats))
                channel_voices[channel].append(beats)
        if len(voices_n_beats) != 1:
            raise ValueError('Voices must have same number of beats')
        n_beats = next(iter(voices_n_beats))
        return cls(channel_voices, n_beats, data.beat_multiplier)

    def to_midi(  # noqa: C901,PLR0912 pylint: disable=too-many-branches
        self,
        *,
        root_note: int,
        bass_note: int | None = None,
        voice_last_message: collections.defaultdict[tuple[str, int], mido.Message] | None = None,
        last_bar: bool = True,
        ticks_per_beat: int = 96,
        midi_channels: dict[str, int] | None = None,
    ) -> dict[tuple[str, int], list[mido.Message]]:
        messages = collections.defaultdict(list)

        if voice_last_message is None:
            voice_last_message = collections.defaultdict(lambda: mido.Message(type='note_off'))

        midi_channels = midi_channels if midi_channels is not None else {}

        for beat_i in range(self.n_beats):
            for channel in self.channels_sorted:
                voices = self.channel_voices[channel]
                midi_channel = midi_channels.get(channel, 0)
                for voice_i, voice in enumerate(voices):
                    last_message = voice_last_message[channel, voice_i]
                    beat_note = voice[beat_i]

                    if beat_note == '--' and last_message.type == 'note_off':
                        raise ValueError('Cannot have -- in the beginning of a voice or after note_off event')

                    if beat_note == '..' and last_message.type == 'note_on':
                        messages[channel, voice_i].append(mido.Message(**last_message.dict() | {'type': 'note_off'}))
                        voice_last_message[channel, voice_i] = messages[channel, voice_i][-1].copy(time=0)
                        if channel == 'bass':
                            bass_note = None
                    if isinstance(beat_note, int):
                        if channel == 'bass':
                            bass_note = root_note + beat_note
                            note = bass_note
                        elif bass_note is None:
                            raise ValueError('bass_note must be set before other channels')
                        else:
                            note = bass_note + beat_note

                        if last_message.type == 'note_off':
                            messages[channel, voice_i].append(mido.Message(type='note_on', note=note, channel=midi_channel, velocity=100, time=last_message.time))
                        elif last_message.type == 'note_on':
                            # messages[channel, voice_i].append(mido.Message(type='note_off', note=last_message.note, velocity=last_message.velocity, time=last_message.time))
                            messages[channel, voice_i].append(mido.Message(**last_message.dict() | {'type': 'note_off'}))
                            messages[channel, voice_i].append(mido.Message(type='note_on', note=note, channel=midi_channel, velocity=100, time=0))
                        voice_last_message[channel, voice_i] = messages[channel, voice_i][-1].copy(time=0)
                    voice_last_message[channel, voice_i].time += int(ticks_per_beat * self.beat_multiplier)
        if last_bar:
            for (channel, voice_i), message in voice_last_message.items():
                if message.type != 'note_on':
                    continue
                messages[channel, voice_i].append(mido.Message(**message.dict() | {'type': 'note_off', 'time': message.time}))
        return messages


class RootNote(ArbitraryTypes):
    root: SpecificNote

    @classmethod
    def from_yaml_data(cls, data: RootNoteData) -> RootNote:
        return cls(root=SpecificNote.from_str(data.root))


class RootTranspose(ArbitraryTypes):
    semitones: int

    @classmethod
    def from_yaml_data(cls, data: RootTransposeData) -> RootTranspose:
        return cls(semitones=data.semitones)


class SkipStart:
    pass


class SkipStop:
    pass


class NotationData(BaseModel):
    model_config = ConfigDict(extra='forbid')
    musiclib_version: str
    events: list[EventData]

    @field_validator('events')
    @classmethod
    def last_event_must_be_bar(cls, v: list[EventData]) -> list[EventData]:
        if v[-1].type != 'Bar':
            raise ValueError('last event must be Bar')
        return v


Event: TypeAlias = (
    Bar
    | RootNote
    | RootTranspose
    | SkipStart
    | SkipStop
)


class Notation:
    def __init__(
        self,
        musiclib_version: str,
        events: list[Event],
    ) -> None:
        if musiclib.__version__ != musiclib_version:
            raise ValueError(f'musiclib must be exact version {musiclib_version} to parse notation')
        self.musiclib_version = musiclib_version
        self.events = events

    @classmethod
    def from_yaml_data(cls, yaml_data: str) -> Notation:
        notation_data = NotationData.model_validate(yaml_data)
        return cls(**notation_data.model_dump(exclude=['events']), events=cls.parse_events(notation_data.events))

    @staticmethod
    def parse_events(events: list[EventData]) -> list[Event]:
        out: list[Event] = []
        for event in events:
            if event.type == 'SkipStart':
                out.append(SkipStart())
                continue
            if event.type == 'SkipStop':
                out.append(SkipStop())
                continue
            cls_data = {
                'RootNote': RootNoteData,
                'RootTranspose': RootTransposeData,
                'Bar': BarData,
            }[event.type]
            event_data_model = cls_data.model_validate(event, from_attributes=True)
            cls = {
                'RootNote': RootNote,
                'RootTranspose': RootTranspose,
                'Bar': Bar,
            }[event_data_model.type]
            out.append(cls.from_yaml_data(event_data_model))  # type: ignore[attr-defined]
        return out

    def to_midi(  # noqa: C901,PLR0912 pylint: disable=too-many-branches
        self,
        *,
        ticks_per_beat: int = 96,
        merge_voices: bool = True,
        midi_channels: dict[str, int] | None = None,
    ) -> mido.MidiFile:
        root_note = None
        bass_note = None
        skip = False

        voice_last_message: collections.defaultdict[tuple[str, int], mido.Message] = collections.defaultdict(lambda: mido.Message(type='note_off'))
        messages: collections.defaultdict[tuple[str, int], list[mido.Message]] = collections.defaultdict(list)

        for event_i, event in enumerate(self.events):
            if isinstance(event, RootNote):
                root_note = event.root.i
            elif isinstance(event, RootTranspose):
                if root_note is None:
                    raise ValueError('Root note was not set before this RootTranspose event')
                root_note += event.semitones
            elif isinstance(event, SkipStart):
                skip = True
            elif isinstance(event, SkipStop):
                skip = False
            elif isinstance(event, Bar):
                if root_note is None:
                    raise ValueError('Root note was not set before this Bar event')
                bar_messages = event.to_midi(
                    root_note=root_note,
                    bass_note=bass_note,
                    voice_last_message=voice_last_message,
                    last_bar=event_i == len(self.events) - 1,
                    ticks_per_beat=ticks_per_beat,
                    midi_channels=midi_channels,
                )
                if ('bass', 0) in bar_messages:
                    bass_note = bar_messages['bass', 0][-1].note
                if skip:
                    continue
                for (channel, voice_i), voice_messages in bar_messages.items():
                    messages[channel, voice_i] += voice_messages
        if merge_voices:
            channel_tracks = collections.defaultdict(list)
            for (channel, voice_i), voice_messages in messages.items():  # noqa: B007
                channel_tracks[channel].append(mido.MidiTrack(voice_messages))
            tracks_merged = [
                [mido.MetaMessage(type='track_name', name=channel), *merge_tracks(tracks, key=lambda msg: (msg.time, {'note_off': 0, 'note_on': 1}.get(msg.type, 3)))]
                for channel, tracks in channel_tracks.items()
            ]
            return mido.MidiFile(tracks=tracks_merged, type=1, ticks_per_beat=ticks_per_beat)
        tracks = [
            mido.MidiTrack([mido.MetaMessage(type='track_name', name=f'{channel}-{voice_i}'), *voice_messages])
            for (channel, voice_i), voice_messages in messages.items()
        ]
        return mido.MidiFile(tracks=tracks, type=1, ticks_per_beat=ticks_per_beat)


def play_file() -> None:
    class StoreDictKeyPair(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None) -> None:  # type: ignore[no-untyped-def] # noqa: ANN001,ARG002
            my_dict = {}
            for kv in values.split(','):
                k, v = kv.split('=')
                my_dict[k] = int(v)
            setattr(namespace, self.dest, my_dict)
    parser = argparse.ArgumentParser()
    parser.add_argument('--bpm', type=float, default=120)
    parser.add_argument('--midi-port', type=str, default='IAC Driver Bus 1', help='MIDI port to send midi messages')
    parser.add_argument('--midi-channels', action=StoreDictKeyPair, help='mapping of instruments to MIDI channels in instrument0:channel0,instrument1:channel1 format')
    parser.add_argument('filepath', type=pathlib.Path)
    args = parser.parse_args()
    yaml_data = yaml.safe_load(args.filepath.read_text())
    nt = Notation.from_yaml_data(yaml_data)
    midi = nt.to_midi(midi_channels=args.midi_channels)
    player = Player(args.midi_port)
    player.play_midi(midi, beats_per_minute=args.bpm)


if __name__ == '__main__':
    play_file()

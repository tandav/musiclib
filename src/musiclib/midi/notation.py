from __future__ import annotations

import argparse
import collections
import pathlib
from typing import Literal
from typing import TypeAlias

import mido
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator

import musiclib
from musiclib.midi.player import Player
from musiclib.note import SpecificNote


class ArbitraryTypes(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class EventData(BaseModel):
    type: Literal['RootChange', 'Bar']
    model_config = ConfigDict(extra='allow')

class RootChangeData(EventData):
    root: str

class BarData(EventData):
    voices: dict[str, list[str]]

class Bar:
    def __init__(self, channel_voices: dict[str, list[list[int | str]]], n_beats: int) -> None:
        self.channel_voices = channel_voices
        self.n_beats = n_beats

    @classmethod
    def from_yaml_data(cls, data: BarData):
        channel_voices = {}
        voices_n_beats = set()
        for channel, voices_str in data.voices.items():
            if channel == 'bass' and len(voices_str) != 1:
                raise ValueError('bass must have only 1 voice')
            channel_voices[channel] = []
            for voice_str in voices_str:
                beats = []
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
        return cls(channel_voices, n_beats)

    def to_midi(
        self,
        root_note: int,
        bass_note: int | None = None,
        voice_last_message: collections.defaultdict | None = None,
        last_bar: bool = True,
        ticks_per_beat: int = 96,
    ):
        messages = collections.defaultdict(list)

        if voice_last_message is None:
            voice_last_message = collections.defaultdict(lambda: mido.Message(type='note_off'))

        # sorting is necessary because bass must be first
        channels_sorted = ['bass'] + sorted(self.channel_voices.keys() - {'bass'})

        for beat_i in range(self.n_beats):
            for channel in channels_sorted:
                voices = self.channel_voices[channel]
                for voice_i, voice in enumerate(voices):
                    last_message = voice_last_message[channel, voice_i]
                    beat_note = voice[beat_i]

                    if beat_note == '--' and last_message.type == 'note_off':
                        raise ValueError('Cannot have -- in the beginning of a voice or after note_off event')

                    if beat_note not in {'..', '--'}:
                        if channel == 'bass':
                            bass_note = root_note + beat_note
                            note = bass_note
                        else:
                            note = bass_note + beat_note

                        if last_message.type == 'note_off':
                            message = mido.Message(type='note_on', note=note, velocity=100, time=last_message.time)
                            messages[channel, voice_i].append(message)
                        elif last_message.type == 'note_on':
                            message = mido.Message(type='note_off', note=last_message.note, velocity=100, time=last_message.time)
                            messages[channel, voice_i].append(message)
                            message = mido.Message(type='note_on', note=note, velocity=100, time=0)
                            messages[channel, voice_i].append(message)
                        voice_last_message[channel, voice_i] = message.copy(time=0)
                    voice_last_message[channel, voice_i].time += ticks_per_beat
        if last_bar:
            for (channel, voice_i), message in voice_last_message.items():
                if message.type != 'note_on':
                    continue
                message = mido.Message(
                    type='note_off',
                    note=last_message.note,
                    velocity=last_message.velocity,
                    channel=last_message.channel,
                    time=ticks_per_beat,
                )
                messages[channel, voice_i].append(message)
        return messages

class RootChange(ArbitraryTypes):
    root: SpecificNote

    @classmethod
    def from_yaml_data(cls, data: RootChangeData):
        return cls(root=SpecificNote.from_str(data.root))


class NotationData(BaseModel):
    model_config = ConfigDict(extra='forbid')
    musiclib_version: str
    events: list[EventData]
    count_from_bass: bool = True

    @field_validator('events')
    @classmethod
    def last_event_must_be_bar(cls, v: list[EventData]) -> list[EventData]:
        if v[-1].type != 'Bar':
            raise ValueError('last event must be Bar')
        return v


Event: TypeAlias = RootChange | Bar


class Notation:
    def __init__(
        self,
        musiclib_version: str,
        events: list[Event],
        count_from_bass: bool = True,
    ):
        if musiclib.__version__ != musiclib_version:
            raise ValueError(f'musiclib must be exact version {musiclib_version} to parse notation')
        self.musiclib_version = musiclib_version
        self.events = events
        self.count_from_bass = count_from_bass

    @classmethod
    def from_yaml_data(cls, yaml_data: str) -> Notation:
        notation_data = NotationData.model_validate(yaml_data)
        return cls(
            **notation_data.model_dump(exclude=['events']),
           events=cls.parse_events(notation_data.events),
        )

    @staticmethod
    def parse_events(events: list[EventData]) -> list[Event]:
        out = []
        for event in events:
            cls_data = {
                'RootChange': RootChangeData,
                'Bar': BarData,
            }[event.type]
            event = cls_data.model_validate(event, from_attributes=True)
            cls = {
                'RootChange': RootChange,
                'Bar': Bar,
            }[event.type]
            out.append(cls.from_yaml_data(event))
        return out

    def to_midi(
        self,
        ticks_per_beat: int = 96,
        merge_voices: bool = True,
    ) -> mido.MidiFile:
        root_note = None
        bass_note = None

        voice_last_message = collections.defaultdict(lambda: mido.Message(type='note_off'))
        messages = collections.defaultdict(list)

        for event_i, event in enumerate(self.events):
            if isinstance(event, RootChange):
                root_note = event.root.i
            elif isinstance(event, Bar):
                if root_note is None:
                    raise ValueError('Root note was not set before this Bar event')
                bar_messages = event.to_midi(
                    root_note=root_note,
                    bass_note=bass_note,
                    voice_last_message=voice_last_message,
                    last_bar=event_i == len(self.events) - 1,
                    ticks_per_beat=ticks_per_beat,
                )
                for (channel, voice_i), voice_messages in bar_messages.items():
                    messages[channel, voice_i] += voice_messages
        if merge_voices:
            channel_tracks = collections.defaultdict(list)
            for (channel, voice_i), voice_messages in messages.items():
                channel_tracks[channel].append(mido.MidiTrack(voice_messages))
            tracks_merged = [
                [mido.MetaMessage(type='track_name', name=channel)] + mido.merge_tracks(tracks)
                for channel, tracks in channel_tracks.items()
            ]
            return mido.MidiFile(tracks=tracks_merged, type=1, ticks_per_beat=ticks_per_beat)
        tracks = [
            mido.MidiTrack([mido.MetaMessage(type='track_name', name=f'{channel}-{voice_i}')] + voice_messages)
            for (channel, voice_i), voice_messages in messages.items()
        ]
        return mido.MidiFile(tracks=tracks, type=1, ticks_per_beat=ticks_per_beat)


def play_file() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--bpm', type=float, default=120)
    parser.add_argument('--midiport', type=str, default='IAC Driver Bus 1')
    parser.add_argument('filepath', type=pathlib.Path)
    args = parser.parse_args()
    code = args.filepath.read_text()
    nt = Notation(code)
    midi = nt.to_midi()
    player = Player(args.midiport)
    player.play_midi(midi, beats_per_minute=args.bpm)


if __name__ == '__main__':
    play_file()

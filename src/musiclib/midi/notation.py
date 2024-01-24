from __future__ import annotations

import argparse
import bisect
import collections
import operator
import pathlib
from typing import Literal
from typing import NamedTuple
from typing import TypeAlias

import mido
import yaml
from mido.midifiles.tracks import _to_reltime
from pydantic import BaseModel
from pydantic import ConfigDict

import musiclib
from musiclib.midi.parse import Midi
from musiclib.midi.parse import MidiNote
from musiclib.midi.parse import abs_messages
from musiclib.midi.player import Player
from musiclib.note import SpecificNote


class IntervalEvent(NamedTuple):
    interval: int
    on: int
    off: int


# class Event:
#     def __init__(self, code: str) -> None:
#         self.type, *_kw = code.splitlines()
#         self.kw = dict(kv.split(maxsplit=1) for kv in _kw)

class ArbitraryTypes(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class EventData(BaseModel):
    type: Literal['RootChange', 'Bar']
    model_config = ConfigDict(extra='allow')

class RootChangeData(EventData):
    root: str

class BarData(EventData):
    voices: list[dict[str, str]]

# class RootChange(Event):
#     def __init__(self, root: SpecificNote) -> None:
#         self.root = SpecificNote.from_str(self.kw['root'])
class RootChange(ArbitraryTypes):
    root: SpecificNote

    @classmethod
    def from_yaml_data(cls, data: RootChangeData):
        return cls(root=SpecificNote.from_str(data.root))



class Voice:
    def __init__(
        self,
        channel: str,
        interval_events: list[IntervalEvent],
    ) -> None:
        self.channel = channel
        self.interval_events = interval_events

    @classmethod
    def from_intervals_str(
        cls,
        channel: str,
        intervals_str: str,
        interval: int | None = None,
        on: int  = 0,
        off: int = 0,
        ticks_per_beat: int = 96,
    ) -> list[IntervalEvent]:
        interval_events = [] 
        for interval_str in intervals_str.split():
            if interval_str == '..':
                if interval is None:
                    on += ticks_per_beat
                else:
                    off += ticks_per_beat
            elif interval_str == '--':
                if interval is None:
                    raise ValueError('Cannot have -- in the beginning of a voice')
                off += ticks_per_beat
            else:
                if interval is not None:
                    interval_events.append(IntervalEvent(interval, on, off))
                    on = off
                off += ticks_per_beat
                interval = int(interval_str, base=12)
        if interval is None:
            raise ValueError('Cannot have empty voice')
        interval_events.append(IntervalEvent(interval, on, off))
        return cls(channel, interval_events)

class Bar(ArbitraryTypes):
    voices: list[Voice]

    @classmethod
    def from_yaml_data(cls, data: BarData):
        voices = []
        for kv in data.voices:
            channel, intervals_str = next(iter(kv.items()))
            voices.append(Voice.from_intervals_str(channel, intervals_str))
        return cls(voices=voices)

    def to_midi(self, root: SpecificNote, *, count_from_bass: bool = True) -> dict[str, list[MidiNote]]:

        # TODO: BAr.to_midi should not exist? dont do here concrete ticks, also in Vouice, Do everything in Notation.to_midi()
        if not isinstance(root, SpecificNote):
            raise TypeError(f'root must be SpecificNote, got {root}')
        channels = collections.defaultdict(list)
        if not count_from_bass:
            for voice in self.voices:
                for interval_event in voice.interval_events:
                    channels[voice.channel].append(
                        MidiNote(
                            note=root + interval_event.interval,
                            on=interval_event.on,
                            off=interval_event.off,
                        ),
                    )
            return dict(channels)
        *voices, bass = self.voices
        for bass_interval_event in bass.interval_events:
            bass_note = root + bass_interval_event.interval
            bass_on = bass_interval_event.on
            bass_off = bass_interval_event.off
            channels[bass.channel].append(MidiNote(on=bass_on, off=bass_off, note=bass_note))

            for voice in voices:
                above_bass_events = voice.interval_events[
                    bisect.bisect_left(voice.interval_events, bass_interval_event.on, key=operator.attrgetter('on')):
                    bisect.bisect_left(voice.interval_events, bass_interval_event.off, key=operator.attrgetter('on'))
                ]

                for interval_event in above_bass_events:
                    channels[voice.channel].append(
                        MidiNote(
                            note=bass_note + interval_event.interval,
                            on=interval_event.on,
                            off=interval_event.off,
                        ),
                    )
        return dict(channels)

class NotationData(BaseModel):
    musiclib_version: str
    ticks_per_beat: int
    midi_channels: list[str]
    events: list[EventData]
    count_from_bass: bool = True,


# class Header:
#     def __init__(
#         self,
#     ) -> None:
# #     def __init__(self, code: str) -> None:
#         super().__init__(code)
#         self.musiclib_version = self.kw['musiclib_version']
#         if musiclib.__version__ != self.musiclib_version:
#             raise ValueError(f'musiclib must be exact version {self.musiclib_version} to parse notation')
#         self.root = SpecificNote.from_str(self.kw['root'])
#         self.ticks_per_beat = int(self.kw['ticks_per_beat'])
#         self.midi_channels = json.loads(self.kw['midi_channels'])




# class RootChange(Event):
#     def __init__(self, code: str) -> None:
#         super().__init__(code)
#         self.root = SpecificNote.from_str(self.kw['root'])


# class Voice:
#     def __init__(self, code: str) -> None:
#         self.channel, intervals_str = code.split(maxsplit=1)
#         self.interval_events = self.parse_interval_events(intervals_str)

#     def parse_interval_events(self, intervals_str: str, ticks_per_beat: int = 96) -> list[IntervalEvent]:
#         interval: int | None = None
#         on = 0
#         off = 0
#         interval_events = []
#         for interval_str in intervals_str.split():
#             if interval_str == '..':
#                 if interval is None:
#                     on += ticks_per_beat
#                 else:
#                     off += ticks_per_beat
#             elif interval_str == '--':
#                 if interval is None:
#                     raise ValueError('Cannot have -- in the beginning of a voice')
#                 off += ticks_per_beat
#             else:
#                 if interval is not None:
#                     interval_events.append(IntervalEvent(interval, on, off))
#                     on = off
#                 off += ticks_per_beat
#                 interval = int(interval_str, base=12)
#         if interval is None:
#             raise ValueError('Cannot have empty voice')
#         interval_events.append(IntervalEvent(interval, on, off))
#         return interval_events


# class Bar:
#     def __init__(self, code: str) -> None:
#         self.voices = [Voice(voice_code) for voice_code in code.splitlines()]



Event: TypeAlias = RootChange | Bar

# class Notation:
#     def __init__(self, code: str) -> None:
#         self.parse(code)
#         self.ticks_per_beat = self.header.ticks_per_beat
#         self.midi_channels = self.header.midi_channels

#     def parse(self, code: str) -> None:
#         self.events: list[Event | Bar] = []
#         for event_code in code.strip().split('\n\n'):
#             if event_code.startswith('header'):
#                 self.header = Header(event_code)
#             elif event_code.startswith('root_change'):
#                 self.events.append(RootChange(event_code))
#             else:
#                 self.events.append(Bar(event_code))

class Notation:
    def __init__(
        self,
        musiclib_version: str,
        ticks_per_beat: int,
        midi_channels: list[int],
        events: list[Event],
        count_from_bass: bool = True,
    ):
        if musiclib.__version__ != musiclib_version:
            raise ValueError(f'musiclib must be exact version {musiclib_version} to parse notation')
        self.musiclib_version = musiclib_version
        self.ticks_per_beat = ticks_per_beat
        self.midi_channels = {channel: i for i, channel in enumerate(midi_channels)}
        self.events = events
        self.count_from_bass = count_from_bass

    @classmethod
    def from_yaml_data(cls, yaml_data: str) -> Notation:
        notation_data = NotationData.model_validate(yaml_data)
        events = cls.parse_events(notation_data.events)
        return cls(
            **notation_data.model_dump(exclude=['events']),
           events=events,
        )
#         return cls(
#             musiclib_version=notation_data.musiclib_version,
#             ticks_per_beat=notation_data.ticks_per_beat,
#             midi_channels=notation_data.midi_channels,
#             events=notation_data.events,
#         )

    @classmethod
    def from_yaml_path(cls, yaml_path: str) -> Notation:
        with open(yaml_path) as f:
            yaml_data = yaml.safe_load(f)
        return cls.from_yaml_data(yaml_data)

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

    def to_midi(self) -> mido.MidiFile:
        channels: list[list[MidiNote]] = [[] for _ in range(len(self.midi_channels))]
        root = None
        t = 0
        for event in self.events:
            if isinstance(event, RootChange):
                root = event.root
            elif isinstance(event, Bar):
                if root is None:
                    raise ValueError('Root was not set before this Bar event')
                bar_midi = event.to_midi(root, count_from_bass=self.count_from_bass)
                bar_off_channels = {channel: notes[-1].off for channel, notes in bar_midi.items()}
                if len(set(bar_off_channels.values())) != 1:
                    raise ValueError(f'all channels in the bar must have equal length, got {bar_off_channels}')
                bar_off = next(iter(bar_off_channels.values()))
                for channel, notes in bar_midi.items():
                    channel_id = self.midi_channels[channel]
                    channels[channel_id] += [
                        MidiNote(
                            note=note.note,
                            on=t + note.on,
                            off=t + note.off,
                            channel=channel_id,
                        )
                        for note in notes
                    ]
                t += bar_off
            else:
                raise TypeError(f'unknown event type: {event}')

        midi_list = [Midi(notes=v, ticks_per_beat=self.ticks_per_beat) for v in channels]
        tracks = [mido.MidiTrack(_to_reltime(abs_messages(midi))) for midi in midi_list]
        return mido.MidiFile(type=1, ticks_per_beat=self.ticks_per_beat, tracks=tracks)


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

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
from pydantic import field_validator

import musiclib
from musiclib.midi.parse import Midi
from musiclib.midi.parse import MidiNote
from musiclib.midi.parse import abs_messages
from musiclib.midi.player import Player
from musiclib.note import SpecificNote


# class IntervalEvent(NamedTuple):
#     interval: int
#     on: int
#     off: int


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
        voice_time: collections.defaultdict | None = None,
        voice_last_message: collections.defaultdict | None = None,
        last_bar: bool = True,
        ticks_per_beat: int = 96,
    ):
        messages = collections.defaultdict(list)

        # todo: try merge: store voice_time info in .time attribute in last_message
        voice_time = voice_time if voice_time is not None else collections.defaultdict(int)
        # voice_last_message = voice_last_message if voice_last_message is not None else collections.defaultdict(lambda: None)
        if voice_last_message is None:
            voice_last_message = collections.defaultdict(lambda: mido.Message(type='note_off'))

        # sorting is necessary because bass must be first
        channels_sorted = ['bass'] + sorted(self.channel_voices.keys() - {'bass'})

        for beat_i in range(self.n_beats):
            for channel in channels_sorted:
                voices = self.channel_voices[channel]
                for voice_i, voice in enumerate(voices):
                    # time = beat_i * ticks_per_beat
                    # voice_time[channel, voice_i] += time
                    # voice_time[channel, voice_i] += ticks_per_beat
                    voice_time[channel, voice_i] = 0 if beat_i == 0 else ticks_per_beat
                    
                    last_message = voice_last_message[channel, voice_i]
                    
                    print('*', voice_time[channel, voice_i], voice_last_message[channel, voice_i])
                    
                    beat_note = voice[beat_i]
                    
                    if beat_note == '--' and last_message.type == 'note_off':
                        raise ValueError('Cannot have -- in the beginning of a voice or after note_off event')
                
                    if beat_note in {'..', '--'}:
                        voice_time[channel, voice_i] += ticks_per_beat
                        continue
                    
                    # time = voice_time[channel, voice_i]
                
                    if channel == 'bass':
                        bass_note = root_note + beat_note
                        note = bass_note
                    else:
                        note = bass_note + beat_note

                    # use midi channel=0 for all tracks
                    if last_message.type == 'note_off':
                        # message = mido.Message(type='note_on', note=note, velocity=100, time=time)
                        message = mido.Message(type='note_on', note=note, velocity=100, time=voice_time[channel, voice_i])
                        messages[channel, voice_i].append(message)
                        voice_last_message[channel, voice_i] = message
                        print(channel, voice_i, message)
                    elif last_message.type == 'note_on':
                        message = mido.Message(type='note_off', note=last_message.note, velocity=100, time=voice_time[channel, voice_i])
                        print(channel, voice_i, message)
                        messages[channel, voice_i].append(message)
                        message = mido.Message(type='note_on', note=note, velocity=100, time=0)
                        print(channel, voice_i, message)
                        messages[channel, voice_i].append(message)
                        voice_last_message[channel, voice_i] = message
                    # voice_time[channel, voice_i] = 0
            
            
        # end last bar
        if last_bar:
            print('end last bar')
            
            for (channel, voice_i), message in voice_last_message.items():
                if message.type != 'note_on':
                    continue
                
                message = mido.Message(
                    type='note_off',
                    note=last_message.note,
                    velocity=last_message.velocity,
                    channel=last_message.channel,
                    time=ticks_per_beat, # todo test on different ending (-- -- -- , .. .. .. etc) some time adjustements may be needed
                )
                print(channel, voice_i, message)
                
                messages[channel, voice_i].append(message)

        return messages

class RootChange(ArbitraryTypes):
    root: SpecificNote

    @classmethod
    def from_yaml_data(cls, data: RootChangeData):
        return cls(root=SpecificNote.from_str(data.root))

# class Bar(ArbitraryTypes):
#     voices: list[str]
 
#     @classmethod
#     def from_yaml_data(cls, data: BarData):
#         voices = []
#         for kv in data.voices:
#             channel, intervals_str = next(iter(kv.items()))
#             voices.append((channel, intervals_str))
#         return cls(voices=voices)

#     @staticmethod
#     def parse_intervals_str(
#         intervals_str: str,
#         interval: int | None = None,
#         on: int  = 0,
#         off: int = 0,
#         ticks_per_beat: int = 96,
#     ) -> list[IntervalEvent]:
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

    # def to_midi(
    #     self,
    #     root: SpecificNote,
    #     channels_state: list[dict],
    #     # t: int = 0,
    #     *,
    #     count_from_bass: bool = True,
    # ) -> dict[str, list[MidiNote]]:

    #     # TODO: BAr.to_midi should not exist? dont do here concrete ticks, also in Vouice, Do everything in Notation.to_midi()
    #     # TODO: dont use MidiNote with .off. Use mido.MidiMessages
    #     #    - what about >1 voices in 1 channel? Accumulate time per channel to compute message time attribute for each channel separately
    #     if not isinstance(root, SpecificNote):
    #         raise TypeError(f'root must be SpecificNote, got {root}')
    #     channels = collections.defaultdict(list)
    #     if not count_from_bass:
    #         for channel, intervals_str in self.voices:
    #             for intervals_str in self.parse_intervals_str(intervals_str):
    #                 channels[channel].append(
    #                     MidiNote(
    #                         note=root + interval_event.interval,
    #                         on=interval_event.on,
    #                         off=interval_event.off,
    #                     ),
    #                 )
    #         return dict(channels)
    #     *voices, bass = self.voices
    #     for bass_interval_event in bass.interval_events:
    #         bass_note = root + bass_interval_event.interval
    #         bass_on = bass_interval_event.on
    #         bass_off = bass_interval_event.off
    #         channels[bass.channel].append(MidiNote(on=bass_on, off=bass_off, note=bass_note))

    #         for voice in voices:
    #             above_bass_events = voice.interval_events[
    #                 bisect.bisect_left(voice.interval_events, bass_interval_event.on, key=operator.attrgetter('on')):
    #                 bisect.bisect_left(voice.interval_events, bass_interval_event.off, key=operator.attrgetter('on'))
    #             ]

    #             for interval_event in above_bass_events:
    #                 channels[voice.channel].append(
    #                     MidiNote(
    #                         note=bass_note + interval_event.interval,
    #                         on=interval_event.on,
    #                         off=interval_event.off,
    #                     ),
    #                 )
    #     return dict(channels)


class NotationData(BaseModel):
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
    ) -> mido.MidiFile:
        root_note = None
        bass_note = None

        voice_time = collections.defaultdict(int)
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
                    voice_time=voice_time,
                    voice_last_message=voice_last_message,
                    last_bar=event_i == len(self.events) - 1,
                    ticks_per_beat=ticks_per_beat,
                )
                for (channel, voice_i), voice_messages in bar_messages.items():
                    messages[channel, voice_i] += voice_messages

        tracks = [
            mido.MidiTrack([mido.MetaMessage(type='track_name', name=f'{channel}-{voice_i}')] + voice_messages)
            for (channel, voice_i), voice_messages in messages.items()
        ]
        return mido.MidiFile(tracks=tracks, type=1, ticks_per_beat=ticks_per_beat)

    # def to_midi(self) -> mido.MidiFile:
    #     channels: list[list[MidiNote]] = [[] for _ in range(len(self.midi_channels))]
    #     channels_time = [[] for _ in range(len(self.midi_channels))]
    #     bass_note = None
    #     root = None
    #     # t = 0
    #     for event in self.events:
    #         if isinstance(event, RootChange):
    #             root = event.root
    #         elif isinstance(event, Bar):
    #             if root is None:
    #                 raise ValueError('Root was not set before this Bar event')
    #             bar_midi = event.to_midi(root, t, count_from_bass=self.count_from_bass)
    #             bar_off_channels = {channel: notes[-1].off for channel, notes in bar_midi.items()}
    #             if len(set(bar_off_channels.values())) != 1:
    #                 raise ValueError(f'all channels in the bar must have equal length, got {bar_off_channels}')
    #             bar_off = next(iter(bar_off_channels.values()))
    #             for channel, notes in bar_midi.items():
    #                 channel_id = self.midi_channels[channel]
    #                 channels[channel_id] += [
    #                     MidiNote(
    #                         note=note.note,
    #                         on=t + note.on,
    #                         off=t + note.off,
    #                         channel=channel_id,
    #                     )
    #                     for note in notes
    #                 ]
    #             t += bar_off
    #         else:
    #             raise TypeError(f'unknown event type: {event}')

    #     midi_list = [Midi(notes=v, ticks_per_beat=self.ticks_per_beat) for v in channels]
    #     tracks = [mido.MidiTrack(_to_reltime(abs_messages(midi))) for midi in midi_list]
    #     return mido.MidiFile(type=1, ticks_per_beat=self.ticks_per_beat, tracks=tracks)


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



# class Voice:
#     def __init__(
#         self,
#         channel: str,
#         interval_events: list[IntervalEvent],
#     ) -> None:
#         self.channel = channel
#         self.interval_events = interval_events

#     @classmethod
#     def from_intervals_str(
#         cls,
#         channel: str,
#         intervals_str: str,
#         interval: int | None = None,
#         on: int  = 0,
#         off: int = 0,
#         ticks_per_beat: int = 96,
#     ) -> list[IntervalEvent]:
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
#         return cls(channel, interval_events)



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
#     def __init__(self, root: SpecificNote) -> None:
#         self.root = SpecificNote.from_str(self.kw['root'])

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

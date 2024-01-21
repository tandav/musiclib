import argparse
import bisect
import collections
import json
import operator
import pathlib
from typing import NamedTuple

import mido
from mido.midifiles.tracks import _to_reltime

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


class Event:
    def __init__(self, code: str) -> None:
        self.type, *_kw = code.splitlines()
        self.kw = dict(kv.split(maxsplit=1) for kv in _kw)


class Header(Event):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.musiclib_version = self.kw['musiclib_version']
        if musiclib.__version__ != self.musiclib_version:
            raise ValueError(f'musiclib must be exact version {self.musiclib_version} to parse notation')
        self.root = SpecificNote.from_str(self.kw['root'])
        self.ticks_per_beat = int(self.kw['ticks_per_beat'])
        self.midi_channels = json.loads(self.kw['midi_channels'])


class Modulation(Event):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.root = SpecificNote.from_str(self.kw['root'])


class Voice:
    def __init__(self, code: str) -> None:
        self.channel, intervals_str = code.split(maxsplit=1)
        self.interval_events = self.parse_interval_events(intervals_str)

    def parse_interval_events(self, intervals_str: str, ticks_per_beat: int = 96) -> list[IntervalEvent]:
        interval: int | None = None
        on = 0
        off = 0
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
        return interval_events


class Bar:
    def __init__(self, code: str) -> None:
        self.voices = [Voice(voice_code) for voice_code in code.splitlines()]

    def to_midi(self, root: SpecificNote, *, figured_bass: bool = True) -> dict[str, list[MidiNote]]:
        if not isinstance(root, SpecificNote):
            raise TypeError(f'root must be SpecificNote, got {root}')
        channels = collections.defaultdict(list)
        if not figured_bass:
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
            channels[bass.channel].append(MidiNote(bass_note, bass_on, bass_off))

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


class Notation:
    def __init__(self, code: str) -> None:
        self.parse(code)
        self.ticks_per_beat = self.header.ticks_per_beat
        self.midi_channels = self.header.midi_channels

    def parse(self, code: str) -> None:
        self.events: list[Event | Bar] = []
        for event_code in code.strip().split('\n\n'):
            if event_code.startswith('header'):
                self.header = Header(event_code)
            elif event_code.startswith('modulation'):
                self.events.append(Modulation(event_code))
            else:
                self.events.append(Bar(event_code))

    def _to_midi(self) -> list[Midi]:
        channels: list[list[MidiNote]] = [[] for _ in range(len(self.header.midi_channels))]
        root = self.header.root
        t = 0
        for event in self.events:
            if isinstance(event, Modulation):
                root = event.root
            elif isinstance(event, Bar):
                bar_midi = event.to_midi(root)
                bar_off_channels = {channel: notes[-1].off for channel, notes in bar_midi.items()}
                if len(set(bar_off_channels.values())) != 1:
                    raise ValueError(f'all channels in the bar must have equal length, got {bar_off_channels}')
                bar_off = next(iter(bar_off_channels.values()))
                for channel, notes in bar_midi.items():
                    channel_id = self.header.midi_channels[channel]
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

        return [Midi(notes=v, ticks_per_beat=self.ticks_per_beat) for v in channels]

    def to_midi(self) -> mido.MidiFile:
        return mido.MidiFile(
            type=1,
            ticks_per_beat=self.ticks_per_beat,
            tracks=[mido.MidiTrack(_to_reltime(abs_messages(midi))) for midi in self._to_midi()],
        )


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

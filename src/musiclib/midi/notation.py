import argparse
import pathlib
import abc
import bisect
import collections
import operator
from typing import NamedTuple

import musiclib
from musiclib.midi.parse import Midi
from musiclib.midi.parse import MidiNote
from musiclib.midi.parse import midiobj_to_midifile
from musiclib.note import SpecificNote
from musiclib.midi.player import Player

import mido


class IntervalEvent(NamedTuple):
    interval: int
    on: int
    off: int


class Event(abc.ABC):
    def __init__(self, code: str):
        self.type, *kw = code.splitlines()
        kw = dict(kv.split(maxsplit=1) for kv in kw)
        self.post_init(**kw)

    def post_init(self, **kw):
        pass


class Header(Event):
    def post_init(
        self,
        version: str,
        root: str,
        ticks_per_beat: str = '96',
    ):
        self.version = version
        self.root = SpecificNote.from_str(root)
        self.ticks_per_beat = int(ticks_per_beat)


class Modulation(Event):
    def post_init(self, root: str):
        self.root = SpecificNote.from_str(root)



class Voice:
    def __init__(self, code: str):
        self.channel, intervals_str = code.split(maxsplit=1)
        self.interval_events = self.parse_interval_events(intervals_str)

    def parse_interval_events(self, intervals_str: str, ticks_per_beat: int = 96):
        interval = None
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
        interval_events.append(IntervalEvent(interval, on, off))
        return interval_events

class Bar:
    def __init__(self, code: str):
        self.voices = [Voice(voice_code) for voice_code in code.splitlines()]

    def to_midi(self, root: SpecificNote, figured_bass: bool = True):
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
        self.ticks_per_beat = self.events[0].ticks_per_beat

    def parse(self, code: str):
        events = code.strip().split('\n\n')
        self.events = [self.parse_event(event) for event in events]

    def parse_event(self, code: str):
        if code.startswith('header'):
            return Header(code)
        if code.startswith('modulation'):
            return Modulation(code)
        return Bar(code)

    def _to_midi(self):
        channels = collections.defaultdict(list)
        root = None
        t = 0
        for event in self.events:
            if isinstance(event, Header):
                root = event.root
                if musiclib.__version__ != event.version:
                    raise ValueError(f'musiclib must be exact version {event.version} to parse notation')
            elif isinstance(event, Modulation):
                root = event.root
            elif isinstance(event, Bar):
                bar_midi = event.to_midi(root)
                bar_off_channels = {channel: notes[-1].off for channel, notes in bar_midi.items()}
                if len(set(bar_off_channels.values())) != 1:
                    raise ValueError(f'all channels in the bar must have equal length, got {bar_off_channels}')
                bar_off = next(iter(bar_off_channels.values()))
                for channel, notes in bar_midi.items():
                    for note in notes:
                        channels[channel].append(MidiNote(note=note.note, on=t+note.on, off=t+note.off))
                t += bar_off
            else:
                raise ValueError(f'unknown event type: {event}')

        channels = {
            k: Midi(notes=v, ticks_per_beat=self.ticks_per_beat)
            for k, v in channels.items()
        }

        return channels

    def to_midi(self):
        tracks = []
        for channel, midi in self._to_midi().items():
            midifile = midiobj_to_midifile(midi)
            track, = midifile.tracks
            tracks.append(track)
        return mido.MidiFile(tracks=tracks, ticks_per_beat=self.ticks_per_beat)


def play_file():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', type=pathlib.Path)
    parser.add_argument('--bpm', type=float, default=120)
    parser.add_argument('--midiport', type=str, default='IAC Driver Bus 1')
    args = parser.parse_args()
    code = args.filepath.read_text()
    nt = Notation(code)
    midi = nt.to_midi()
    player = Player(args.midiport)
    player.play_midi(midi, beats_per_minute=args.bpm)


if __name__ == '__main__':
    play_file()

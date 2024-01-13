import abc
from typing import NamedTuple
from musiclib.note import SpecificNote
from musiclib.intervalset import IntervalSet


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
        intervalset: str,
        ticks_per_beat: str = '96',
    ):
        self.version = version
        self.root = SpecificNote.from_str(root)
        self.intervalset = IntervalSet.from_name(intervalset)
        self.ticks_per_beat = int(ticks_per_beat)
                    

class Modulation(Event):
    def post_init(self, root: str, intervalset: str):
        self.root = SpecificNote.from_str(root)
        self.intervalset = IntervalSet.from_name(intervalset)
                        


class Voice:
    def __init__(self, code: str):
        self.name, intervals_str = code.split(maxsplit=1)
        self.intervals = self.parse_intervals(intervals_str)
        
    def parse_intervals(self, intervals_str: str, ticks_per_beat: int = 96):
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
        return interval_events

class Bar:
    def __init__(self, code: str):
        self.voices = [Voice(voice_code) for voice_code in code.splitlines()]


class Notation:
    def __init__(self, code: str) -> None:
        self.parse(code)
    
    def parse(self, code: str):
        events = code.strip().split('\n\n')
        self.events = [self.parse_event(event) for event in events]
        
    def parse_event(self, code: str):
        if code.startswith('header'):
            return Header(code)
        if code.startswith('modulation'):
            return Modulation(code)
        return Bar(code)

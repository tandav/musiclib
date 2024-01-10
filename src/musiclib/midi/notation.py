from musiclib.note import SpecificNote
from musiclib.intervalset import IntervalSet


class Header:
    def __init__(self, code: str):
        for line in code.strip().splitlines():
            k, v = line.split()
            if k == 'version':
                self.version = v
            elif k == 'root':
                self.root = SpecificNote.from_str(v)
            elif k == 'intervalset':
                self.intervalset = IntervalSet.from_name(v)
                    

class Modulation:
    def __init__(self, code: str):
        _, *kvs = code.splitlines()
        for kv in kvs:
            k, v = kv.split(maxsplit=1)
            if k == 'root':
                self.root = SpecificNote.from_str(v)
            elif k == 'intervalset':
                self.intervalset = IntervalSet.from_name(v)
                        
class Voice:
    def __init__(self, code: str, n_intervals: int = 16):
        i = -n_intervals * 4
        self.name = code[:i].strip()
        intervals_str = code[i:]
        self.intervals = self.parse_intervals(intervals_str)

    def parse_intervals(self, intervals_str: str) -> list[int | None]:
        div, mod = divmod(len(intervals_str), 4)
        if mod != 0:
            raise ValueError(f'intervals_str should be a multiple of 4, got {intervals_str}')
        intervals = []
        for i in range(div):
            interval_str = intervals_str[i * 4:(i + 1) * 4]
            if interval_str == '    ':
                interval = None
            else:
                interval = int(interval_str, base=12)
            intervals.append(interval)
        return intervals


class Bar:
    def __init__(self, code: str):
        self.voices = [Voice(voice_code) for voice_code in code.splitlines()]


class Notation:
    def __init__(self, code: str) -> None:
        self.parse(code)
    
    def parse(self, code: str):
        header, *events = code.strip().split('\n\n')
        self.header = Header(header)
        self.events = [self.parse_event(event) for event in events]
        
    def parse_event(self, code: str):
        if code.startswith('modulation'):
            return Modulation(code)
        return Bar(code)

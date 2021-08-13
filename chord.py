import functools
import itertools
import config

class Chord:
    def __init__(self, str_chord: str):
        self.str_chord = str_chord
        self.add_kind()

    def add_kind(self):
        it = itertools.cycle(config.chromatic_notes)
        it = itertools.dropwhile(lambda x: x != self.str_chord[0], it)
        it = enumerate(it)
        it = filter(lambda kv: kv[1] in self.str_chord, it)
        it = itertools.islice(it, 3)
        it = list(it)
        intervals = tuple(k for k, v in it[1:])
        self.kind = {(3, 7): 'min', (4, 7): 'maj', (3, 6): 'dim'}[intervals]

    def __eq__(self, other): return self.str_chord == other.str_chord
    def __hash__(self): return hash(self.str_chord)

    def __str__(self):
        return self.str_chord

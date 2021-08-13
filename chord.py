import functools
import itertools
import config
from piano import chord_to_piano

class Chord:
    def __init__(self, str_chord: str):
        self.str_chord = str_chord
        self.root = str_chord[0]
        self.add_name()

    def add_name(self):
        it = itertools.cycle(config.chromatic_notes)
        it = itertools.dropwhile(lambda x: x != self.str_chord[0], it)
        it = enumerate(it)
        it = filter(lambda kv: kv[1] in self.str_chord, it)
        it = itertools.islice(it, 3)
        it = list(it)
        intervals = tuple(k for k, v in it[1:])
        self.name = {(3, 7): 'minor', (4, 7): 'major', (3, 6): 'diminished'}[intervals]

    def __eq__(self, other): return self.str_chord == other.str_chord
    def __hash__(self): return hash(self.str_chord)
    def __getitem__(self, item): return self.str_chord[item]
    def __len__(self): return len(self.str_chord)

    def __str__(self):
        return self.str_chord

    def to_piano_image(self, base64=False):
        return chord_to_piano(self, as_base64=base64)

    # def _repr_html_(self):
    def __repr__(self):
        label = hasattr(self, 'label') and f"id={self.label!r}"or ''

        return f'''
        <li class='card {self.name}' >
        <span class='card_header' {label} ><h3>{self.root} {self.name}</h3></span>
        <img src='{self.to_piano_image(base64=True)}'/>
        </li>
        '''


class LabeledChord(Chord):
    pass
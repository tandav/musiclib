from collections import deque, defaultdict
import itertools
import functools
import textwrap
import config
import util
from piano import scale_to_piano
from chord import Chord



def chromatic(tonic):
    notes = deque(config.chromatic_notes)
    while notes[0] != tonic:
        notes.rotate(1)
    return notes


def scale_notes(tonic, bits):
    # return itertools.compress(chromatic(tonic), bits | Map(int)) | Pipe(''.join)
    return ''.join(itertools.compress(chromatic(tonic), map(int, bits)))


class Scale:
    def __init__(self, root: str, name: str):
        self.root = root
        self.bits = config.name_2_bits[name]
        self.name = name
        self.notes = scale_notes(root, self.bits)
        self.kind = config.kinds.get(name)
        if self.kind == 'diatonic':
            self.add_chords()
        self.add_as_C()
        self.is_selected = False


    def add_as_C(self):
        self.as_C = ''
        for bits, name in config.bits_2_name.items():
            if set(self.notes) == set(scale_notes(config.chromatic_notes[0], bits)):
                self.as_C = name

    @classmethod
    def from_bits(cls, root: str, bits: str):
        return cls(root, config.bits_2_name[bits])


    def add_chords(self):
        notes_deque = deque(self.notes)
        self.chords = list()

        while True:
            chord = Chord(notes_deque[0] + notes_deque[2] + notes_deque[4])
            if chord in self.chords:
                return
            self.chords.append(chord)
            notes_deque.rotate(-1)


    @property
    def notes_scale_colors(self):
        return [
            util.hex_to_rgb(config.scale_colors[scale])
            for scale in util.iter_scales(self.kind, start=self.name)
        ]


    def to_piano_image(self, base64=False):
        return scale_to_piano(
            self.notes, self.notes_scale_colors, as_base64=base64,
            green_notes=getattr(self, 'new_notes', frozenset()),
            red_notes=getattr(self, 'del_notes', frozenset()),
        )

    def _chords_text(self):
        x = 'chords:\n'
        for i, chord in enumerate(self.chords, start=1):
            x += f'{i} {chord} {chord.name}\n'
        return x

    def selected_repr(self):
        self.is_selected = True
        r = repr(self)
        self.is_selected = False
        return r

    # @functools.cached_property
    def __repr__(self):
        # <code>bits: {self.bits}</code><br>
        as_C = self.as_C and f'as_C: {self.as_C}' or ''
        chords_hover = f"title='{self._chords_text()}'" if self.kind =='diatonic' else ''
        is_selected = 'selected_scale' if self.is_selected else ''

        return f'''
        <div class='card {self.name} {is_selected}' {chords_hover}>
        <a href='/{self.kind}/{self.root}/{self.name}'>
        <span class='card_header'><h3>{self.root} {self.name}</h3><span class='as_c'>{as_C}</span></span>
        <img src='{self.to_piano_image(base64=True)}'/>
        </a>
        </div>
        '''

    @property
    def key(self):
        return self.root, self.name

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)



class ComparedScale(Scale):
    '''
    this is compared scale
    local terminology: left sclae is compared to right
    left is kinda parent, right is kinda child
    '''
    def __init__(self, left: Scale, right: Scale):
        super().__init__(right.root, right.name)
        self.shared_notes = util.sort_notes(frozenset(left.notes) & frozenset(self.notes))
        self.new_notes = frozenset(self.notes) - frozenset(left.notes)
        self.del_notes = frozenset(left.notes) - frozenset(self.notes)
        if self.kind == 'diatonic':
            self.shared_chords = frozenset(left.chords) & frozenset(self.chords)
        self.left = left


    def _shared_chords_text(self):
        x = 'shared chords:\n'
        for i, chord in enumerate(self.chords, start=1):
            shared_info = chord in self.shared_chords and f'shared, was {self.left.chords.index(chord) + 1}' or ''
            x += f"{i} {chord} {chord.name} {shared_info}\n"
        return x

    def __repr__(self):
        # <code>bits: {self.bits}</code><br>
        as_C = self.as_C and f'as_C: {self.as_C}' or ''
        chords_hover = f"title='{self._shared_chords_text()}'" if self.kind == 'diatonic' else ''
        if self.kind == 'diatonic':
            return f'''
            <a href='/{self.kind}/{self.left.root}/{self.left.name}/compare_to/{self.root}/{self.name}'>
            <div class='card {self.name}' {chords_hover}>
            <span class='card_header'><h3>{self.root} {self.name}</h3><span class='as_c'>{as_C}</span></span>
            <img src='{self.to_piano_image(base64=True)}'/>
            </a>
            </div>
            '''
        else:
            return f'''
            <div class='card {self.name}' {chords_hover}>
            <span class='card_header'><h3>{self.root} {self.name}</h3><span class='as_c'>{as_C}</span></span>
            <img src='{self.to_piano_image(base64=True)}'/>
            </div>
            '''


all_scales = {
    'diatonic'  : {(root, name): Scale(root, name) for root, name in itertools.product(config.chromatic_notes, config.diatonic)},
    'pentatonic': {(root, name): Scale(root, name) for root, name in itertools.product(config.chromatic_notes, config.pentatonic)},
}


@functools.lru_cache(maxsize=1024)
def neighbors(left: Scale):
    neighs = defaultdict(list)
    for right in all_scales[left.kind].values():
        if left == right:
            continue
        right = ComparedScale(left, right)
        neighs[len(right.shared_notes)].append(right)
    return neighs


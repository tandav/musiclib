from collections import deque, defaultdict
import itertools
import functools
import textwrap
import config
import util
from piano import scale_to_piano


name_2_bits = {
    'major'     : '101011010101',
    'dorian'    : '101101010110',
    'phrygian'  : '110101011010',
    'lydian'    : '101010110101',
    'mixolydian': '101011010110',
    'minor'     : '101101011010',
    'locrian'   : '110101101010',
}

bits_2_name = {
    '101011010101': 'major',
    '101101010110': 'dorian',
    '110101011010': 'phrygian',
    '101010110101': 'lydian',
    '101011010110': 'mixolydian',
    '101101011010': 'minor',
    '110101101010': 'locrian',
}

def chromatic(tonic):
    notes = deque(config.chromatic_notes)
    while notes[0] != tonic:
        notes.rotate(1)
    return notes


def scale_notes(tonic, bits):
    # return itertools.compress(chromatic(tonic), bits | Map(int)) | Pipe(''.join)
    return ''.join(itertools.compress(chromatic(tonic), map(int, bits)))


@functools.lru_cache(1024)
def chord_kind(chord):
    it = itertools.cycle(config.chromatic_notes)
    it = itertools.dropwhile(lambda x: x != chord[0], it)
    it = enumerate(it)
    # it = itertools.compress(it, (0))
    it = filter(lambda kv: kv[1] in chord, it)
    it = itertools.islice(it, 3)
    it = list(it)
    intervals = tuple(k for k, v in it[1:])
    return {(3, 7): 'min', (4, 7): 'maj', (3, 6): 'dim'}[intervals]


class Scale:
    def __init__(self, root: str, name: str):
        self.root = root
        self.bits = name_2_bits[name]
        self.name = name
        self.notes = scale_notes(root, self.bits)
        self.add_chords()
        self.add_as_C()


    def add_as_C(self):
        self.as_C = ''
        for bits, name in bits_2_name.items():
            if set(self.notes) == set(scale_notes(config.chromatic_notes[0], bits)):
                self.as_C = name


    @classmethod
    def from_bits(cls, root: str, bits: str):
        return cls(root, bits_2_name[bits])


    def add_chords(self):
        notes_deque = deque(self.notes)
        self.chords = list()

        while True:
            chord = notes_deque[0] + notes_deque[2] + notes_deque[4]
            if chord in self.chords:
                return
            self.chords.append(chord)
            notes_deque.rotate(-1)


    def to_piano_image(self, base64=False):
        return scale_to_piano(
            self.notes, as_base64=base64,
            green_notes=getattr(self, 'new_notes', frozenset()),
            red_notes=getattr(self, 'del_notes', frozenset()),
        )

    def _chords_text(self):
        x = 'chords:\n'
        for i, chord in enumerate(self.chords, start=1):
            x += f'{i} {chord} {chord_kind(chord)}\n'
        return x


    # @functools.cached_property
    def to_html(self):
        # <code>bits: {self.bits}</code><br>
        as_C = self.as_C and f'as_C: {self.as_C}' or ''
        return f'''
        <div class='scale {self.name}' title='{self._chords_text()}'>
        <span class='scale_header'><h3><a href='/scale/{self.root}/{self.name}'>{self.root} {self.name}</a></h3><span>{as_C}</span></span>
        <img src='{self.to_piano_image(base64=True)}'/>
        </div>
        '''

    @property
    def key(self):
        return self.root, self.name

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)


    def __repr__(self):
        return f"Scale(tonic={self.root!r}, name={self.name!r:<12}, notes={self.notes!r} as_C={self.as_C:<12})"
#         return textwrap.dedent(f'''\
#         {self.root}     {self.name:<12}
#         notes {self.notes}
#         as_C  {self.as_C}
#         ''')


class ComparedScale(Scale):
    '''
    this is compared scale
    local terminology: left sclae is compared to right
    left is kinda parent, right is kinda child
    '''
    def __init__(self, root, name, left: Scale):
        super().__init__(root, name)
        self.shared_notes = util.sort_notes(frozenset(left.notes) & frozenset(self.notes))
        self.new_notes = frozenset(self.notes) - frozenset(left.notes)
        self.del_notes = frozenset(left.notes) - frozenset(self.notes)
        self.shared_chords = frozenset(left.chords) & frozenset(self.chords)
        self.left = left


    def _shared_chords_text(self):
        x = 'shared chords:\n'
        for i, chord in enumerate(self.chords, start=1):
            shared_info = chord in self.shared_chords and f'shared, was {self.left.chords.index(chord) + 1}' or ''
            x += f"{i} {chord} {chord_kind(chord)} {shared_info}\n"
        return x

    def to_html(self):
        # <code>bits: {self.bits}</code><br>
        as_C = self.as_C and f'as_C: {self.as_C}' or ''

        return f'''
        <div class='scale {self.name}' title='{self._shared_chords_text()}'>
        <span class='scale_header'><h3><a href='/scale/{self.root}/{self.name}'>{self.root} {self.name}</a></h3><span>{as_C}</span></span>
        <img src='{self.to_piano_image(base64=True)}'/>
        </div>
        '''

all_scales = {(root, name): Scale(root, name) for root, name in itertools.product(config.chromatic_notes, name_2_bits)}

@functools.lru_cache(maxsize=1024)
def neighbors(left):
    neighs = defaultdict(list)
    for s in all_scales.values():
        if s == left:
            continue
        right = ComparedScale(s.root, s.name, left)
        neighs[len(right.shared_notes)].append(right)
    return neighs


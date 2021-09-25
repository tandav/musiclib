import functools
import itertools
from collections import defaultdict
from collections import deque
from typing import Union

from . import chromatic
from . import config
from . import util
from .chord import Chord
from .note import Note
from .piano import Piano

bits_2_name = {
    '101011010101': 'major',
    '101101010110': 'dorian',
    '110101011010': 'phrygian',
    '101010110101': 'lydian',
    '101011010110': 'mixolydian',
    '101101011010': 'minor',
    '110101101010': 'locrian',

    '101010010100': 'p_major',
    '101001010010': 'p_dorian',
    '100101001010': 'p_phrygian',
    '101001010100': 'p_mixolydian',
    '100101010010': 'p_minor',

    '101011010100': 's_major',
    '101101010010': 's_dorian',
    '110101001010': 's_phrygian',
    '101010010101': 's_lydian',
    '101001010110': 's_mixolydian',
    '100101011010': 's_minor',
}

name_2_bits = {v: k for k, v in bits_2_name.items()}


class Scale:
    def __init__(self, root: Union[str, Note], name: str):
        if isinstance(root, str):
            root = Note(root)
        self.root = root
        self.name = name
        self.key = root, name
        self.bits = name_2_bits[name]
        self.notes = tuple(itertools.compress(chromatic.iterate(start_note=root), map(int, self.bits)))

        # self.notes = tuple(itertools.compress(chromatic(root), map(int, self.bits)))
        # print(self.notes)
        self.chromatic_mask = ''.join(note.name if note in self.notes else '_' for note in chromatic.iterate(take_n=12))
        # self.chromatic_bits = ''.join(str(int(note in self.notes)) for note in config.chromatic_notes) # from C (config.chromatic_notes[0])
        # self.chromatic_bits = int(self.bits, base=2)
        self.kind = config.kinds.get(name)
        if self.kind == 'diatonic':
            self.add_chords()
        self.note_colors = {
            note: util.hex_to_rgb(config.scale_colors[scale])
            for note, scale in zip(self.notes, util.iter_scales(self.kind, start=self.name))
        }
        self.html_classes = ('card', self.name)

    def add_chords(self):
        notes_deque = deque(self.notes)
        chords = []
        for _ in range(len(notes_deque)):
            chord = Chord(frozenset({notes_deque[0], notes_deque[2], notes_deque[4]}), root=notes_deque[0])
            chords.append(chord)
            notes_deque.rotate(-1)
        self.chords = tuple(chords)

    def to_piano_image(self):
        return Piano(scale=self)._repr_svg_()

    def _chords_text(self):
        x = 'chords:\n'
        for i, chord in enumerate(self.chords, start=1):
            x += f'{i} {chord} {chord.name}\n'
        return x

    def with_html_classes(self, classes: tuple):
        prev = self.html_classes
        self.html_classes = prev + classes
        r = self._repr_html_()
        self.html_classes = prev
        return r

    # def __format__(self, format_spec): raise No

    # @functools.cached_property
    def _repr_html_(self):
        # <code>bits: {self.bits}</code><br>
        # chords_hover = f"title='{self._chords_text()}'" if self.kind =='diatonic' else ''
        chords_hover = ''
        return f'''
        <div class='{' '.join(self.html_classes)}' {chords_hover}>
        <a href='/circle/{self.root.name}'><span class='card_header'><h3>{self.root.name} {self.name}</h3></span></a>
        {self.to_piano_image()}
        </div>
        '''

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)
    def __repr__(self): return f'Scale({self.root} {self.name})'


class ComparedScale(Scale):
    '''
    this is compared scale
    local terminology: left sclae is compared to right
    left is kinda parent, right is kinda child
    '''
    def __init__(self, left: Scale, right: Scale):
        super().__init__(right.root, right.name)
        self.shared_notes = frozenset(left.notes) & frozenset(self.notes)
        self.new_notes = frozenset(self.notes) - frozenset(left.notes)
        self.del_notes = frozenset(left.notes) - frozenset(self.notes)
        if self.kind == 'diatonic':
            self.shared_chords = frozenset(left.chords) & frozenset(self.chords)
        self.left = left
        self.right = right  # clean
        self.key = left, right

    def to_piano_image(self, as_base64=False):

        return Piano(
            scale=self,
            red_notes=self.del_notes, green_notes=self.new_notes, blue_notes=self.shared_notes,
            notes_squares={
                chord.root: (
                    config.chord_colors[chord.name],
                    config.BLUE_COLOR if chord in self.shared_chords else config.BLACK_COLOR,
                    config.BLUE_COLOR if chord in self.shared_chords else config.BLACK_COLOR,
                    chord.str_chord,
                )
                for chord in self.chords
            },
        )._repr_svg_()

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)
    def __repr__(self): return f'ComparedScale({self.left.root} {self.left.name} | {self.right.root} {self.right.name})'


diatonic = {(root, name): Scale(root, name) for root, name in itertools.product(config.chromatic_notes, config.diatonic)}
pentatonic = {(root, name): Scale(root, name) for root, name in itertools.product(config.chromatic_notes, config.pentatonic)}
all_scales = {'diatonic': diatonic, 'pentatonic': pentatonic}

# circle of fifths clockwise
majors = tuple(diatonic[note, 'major'] for note in 'CGDAEBfdaebF')


@functools.cache
def neighbors(left: Scale):
    neighs = defaultdict(list)
    for right in all_scales[left.kind].values():
        # if left == right:
        #     continue
        right = ComparedScale(left, right)
        neighs[len(right.shared_notes)].append(right)
    return neighs


def print_neighbors(s: Scale):
    neighs = neighbors(s)
    for n_intersect in sorted(neighs.keys(), reverse=True):
        for n in neighs[n_intersect]:
            if n.name != 'major': continue
            print(repr(n).ljust(32), '|', end=' ')
            for note in n.chromatic_mask:
                if note in s.chromatic_mask: print(util.cprint(note, color='BLUE'), end='')
                else: print(note, end='')
            print(' |', end=' ')
            for chord in n.chords:
                if chord in n.shared_chords: print(util.cprint(chord, color='BLUE'), end=' ')
                else: print(chord, end=' ')
            print()
        print('=' * 100)

# warm up cache
# for scale in tqdm.tqdm(tuple(itertools.chain(all_scales['diatonic'].values(), all_scales['pentatonic'].values()))):
#     _ = scale.to_piano_image(as_base64=True)
#     for neighbor in itertools.chain.from_iterable(neighbors(scale).values()):
#         _ = neighbor.to_piano_image(as_base64=True)

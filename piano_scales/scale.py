from collections import deque, defaultdict
import itertools
import functools
import tqdm
from . import config, util
from .piano import Piano
from .chord import Chord
from collections.abc import Iterable



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
        self.bits_from_root = config.name_2_bits[name]
        self.name = name
        self.notes = scale_notes(root, self.bits_from_root)
        self.bits = ''.join(str(int(note in self.notes)) for note in config.chromatic_notes) # from C (config.chromatic_notes[0])
        self.bits_int = int(self.bits, base=2)
        self.kind = config.kinds.get(name)
        if self.kind == 'diatonic':
            self.add_chords()
        self.note_colors = {
            note: util.hex_to_rgb(config.scale_colors[scale])
            for note, scale in zip(self.notes, util.iter_scales(self.kind, start=self.name))
        }
        self.html_classes = ('card', self.name)


    # @classmethod
    # def from_bits(cls, root: str, bits: str):
    #     return cls(root, config.bits_2_name[bits])


    def add_chords(self):
        notes_deque = deque(self.notes)
        self.chords = list()

        while True:
            chord = Chord(notes_deque[0] + notes_deque[2] + notes_deque[4])
            if chord in self.chords:
                break
            self.chords.append(chord)
            notes_deque.rotate(-1)
        self.chords = tuple(self.chords)


    # def to_piano_image(self, as_base64=False):
    #     return scale_to_piano(self.notes, self.chords, self.notes_scale_colors, as_base64=as_base64)

    def to_piano_image(self):
        return Piano(scale=self)._repr_html_()
    #     if self.kind == 'diatonic':
    #         return scale_to_piano(
    #             self.notes, self.chords, self.notes_scale_colors,
    #             as_base64=as_base64,
    #         )
    #     else:
    #         return scale_to_piano(
    #             self.notes, None, self.notes_scale_colors,
    #             as_base64=as_base64,
    #         )


    def _chords_text(self):
        x = 'chords:\n'
        for i, chord in enumerate(self.chords, start=1):
            x += f'{i} {chord} {chord.name}\n'
        return x

    def with_html_classes(self, classes: tuple):
        prev = self.html_classes
        self.html_classes = prev + classes
        r = repr(self)
        self.html_classes = prev
        return r

    # def __format__(self, format_spec): raise No

    # @functools.cached_property
    def __repr__(self):
        # <code>bits: {self.bits}</code><br>
        # chords_hover = f"title='{self._chords_text()}'" if self.kind =='diatonic' else ''
        chords_hover = ''
        return f'''
        <div class='{' '.join(self.html_classes)}' {chords_hover}>
        <a href='/{self.kind}/{self.root}/{self.name}'>
        <span class='card_header'><h3>{self.root} {self.name}</h3></span>
        {self.to_piano_image()}
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
        self.right = right # clean

    def to_piano_image(self, as_base64=False):
        return Piano(scale=self)
        # if self.kind == 'diatonic':
        #     return scale_to_piano(
        #         self.notes, self.chords, self.notes_scale_colors,
        #         green_notes=self.new_notes, red_notes=self.del_notes, shared_chords=self.shared_chords,
        #         as_base64=as_base64,
        #     )
        # else:
        #     return scale_to_piano(
        #         self.notes, None, self.notes_scale_colors,
        #         green_notes=self.new_notes, red_notes=self.del_notes, shared_chords=None,
        #         as_base64=as_base64,
        #     )

    def _shared_chords_text(self):
        x = 'shared chords:\n'
        for i, chord in enumerate(self.chords, start=1):
            shared_info = chord in self.shared_chords and f'shared, was {self.left.chords.index(chord) + 1}' or ''
            x += f"{i} {chord} {chord.name} {shared_info}\n"
        return x

    def __repr__(self):
        # <code>bits: {self.bits}</code><br>
        chords_hover = f"title='{self._shared_chords_text()}'" if self.kind == 'diatonic' else ''
        if self.kind == 'diatonic':
            return f'''
            <a href='/{self.kind}/{self.left.root}/{self.left.name}/compare_to/{self.root}/{self.name}'>
            <div class='card {self.name}' {chords_hover}>
            <span class='card_header'><h3>{self.root} {self.name}</h3></span>
            <img src='{self.to_piano_image(as_base64=True)}'/>
            </a>
            </div>
            '''
        else:
            return f'''
            <div class='card {self.name}' {chords_hover}>
            <span class='card_header'><h3>{self.root} {self.name}</h3></span>
            <img src='{self.to_piano_image(as_base64=True)}'/>
            </div>
            '''
    @property
    def key(self):
        return self.left, self.right

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)


all_scales = {
    'diatonic'  : {(root, name): Scale(root, name) for root, name in itertools.product(config.chromatic_notes, config.diatonic)},
    'pentatonic': {(root, name): Scale(root, name) for root, name in itertools.product(config.chromatic_notes, config.pentatonic)},
}

# majors = [s for s in all_scales['diatonic'].values() if s.name == 'major']

# circle of fifths clockwise
majors = tuple(all_scales['diatonic'][note, 'major'] for note in 'CGDAEBfdaebF')



@functools.lru_cache(maxsize=1024)
def neighbors(left: Scale):
    neighs = defaultdict(list)
    for right in all_scales[left.kind].values():
        if left == right:
            continue
        right = ComparedScale(left, right)
        neighs[len(right.shared_notes)].append(right)
    return neighs

# warm up cache
# for scale in tqdm.tqdm(tuple(itertools.chain(all_scales['diatonic'].values(), all_scales['pentatonic'].values()))):
#     _ = scale.to_piano_image(as_base64=True)
#     for neighbor in itertools.chain.from_iterable(neighbors(scale).values()):
#         _ = neighbor.to_piano_image(as_base64=True)


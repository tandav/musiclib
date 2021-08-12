from collections import deque, defaultdict
import itertools
import config
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



class Scale:
    def __init__(self, root, name):
        self.root = root
        self.bits = name_2_bits[name]
        self.name = name
        self.notes = scale_notes(root, self.bits)
        self.as_C = ''

        for bits, name in bits_2_name.items():
            if set(self.notes) == set(scale_notes(config.chromatic_notes[0], bits)):
                self.as_C = name

    @classmethod
    def from_bits(cls, tonic, bits):
        return cls(tonic, bits_2_name[bits])

    def to_piano_image(self, base64=False):
        return scale_to_piano(self.notes, as_base64=base64)

    def to_html(self):
        # <code>bits: {self.bits}</code><br>
        as_C = self.as_C and f'as_C: {self.as_C}' or ''
        return f'''
        <div class='scale {self.name}'>
        <span class='scale_header'><h3><a href='/scale/{self.root}/{self.name}'>{self.root} {self.name}</a></h3><span>{as_C}</span></span>
        <img src='{self.to_piano_image(base64=True)}'/>
        </div>
        '''

    def __eq__(self, other):
        return self.root == other.root and self.name == other.name

    def __repr__(self):
        return f"Scale(tonic={self.root!r}, name={self.name!r:<12}, notes={self.notes!r} as_C={self.as_C:<12})"
#         return textwrap.dedent(f'''\
#         {self.root}     {self.name:<12}
#         notes {self.notes}
#         as_C  {self.as_C}
#         ''')




all_scales = {(root, name): Scale(root, name) for root, name in itertools.product(config.chromatic_notes, name_2_bits)}

def neighbors(scale):
    neighs = defaultdict(list)
    for s in all_scales.values():
        if s == scale:
            continue
        shared = ''.join(sorted(set(scale.notes) & set(s.notes), key=config.chromatic_notes.find))
        neighs[len(shared)].append(s)
    return neighs


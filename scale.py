from collections import deque
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


    def __repr__(self):
        return f"Scale(tonic={self.root!r}, name={self.name!r:<12}, notes={self.notes!r} as_C={self.as_C:<12})"
#         return textwrap.dedent(f'''\
#         {self.root}     {self.name:<12}
#         notes {self.notes}
#         as_C  {self.as_C}
#         ''')
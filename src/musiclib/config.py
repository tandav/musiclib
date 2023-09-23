import functools
import itertools
import operator
from colortool import Color
from musiclib.util.etc import named_intervals_rotations

chromatic_notes = 'CdDeEFfGaAbB'  # TODO make variable here, delete from config, reimport everywhere, maybe circular imports



name_to_intervals_kind_grouped = {
    'natural': {
        'major': frozenset({0, 2, 4, 5, 7, 9, 11}),
        'dorian': frozenset({0, 2, 3, 5, 7, 9, 10}),
        'phrygian': frozenset({0, 1, 3, 5, 7, 8, 10}),
        'lydian': frozenset({0, 2, 4, 6, 7, 9, 11}),
        'mixolydian': frozenset({0, 2, 4, 5, 7, 9, 10}),
        'minor': frozenset({0, 2, 3, 5, 7, 8, 10}),
        'locrian': frozenset({0, 1, 3, 5, 6, 8, 10}),
    },
    'harmonic': {
        'h_minor': frozenset({0, 2, 3, 5, 7, 8, 11}),
        'h_locrian': frozenset({0, 1, 3, 5, 6, 9, 10}),
        'h_major': frozenset({0, 2, 4, 5, 8, 9, 11}),
        'h_dorian': frozenset({0, 2, 3, 6, 7, 9, 10}),
        'h_phrygian': frozenset({0, 1, 4, 5, 7, 8, 10}),
        'h_lydian': frozenset({0, 3, 4, 6, 7, 9, 11}),
        'h_mixolydian': frozenset({0, 1, 3, 4, 6, 8, 9}),
    },
    'melodic': {
        'm_minor': frozenset({0, 2, 3, 5, 7, 9, 11}),
        'm_locrian': frozenset({0, 1, 3, 5, 7, 9, 10}),
        'm_major': frozenset({0, 2, 4, 6, 8, 9, 11}),
        'm_dorian': frozenset({0, 2, 4, 6, 7, 9, 10}),
        'm_phrygian': frozenset({0, 2, 4, 5, 7, 8, 10}),
        'm_lydian': frozenset({0, 2, 3, 5, 6, 8, 10}),
        'm_mixolydian': frozenset({0, 1, 3, 4, 6, 8, 10}),
    },
    'pentatonic': {
        'p_major': frozenset({0, 2, 4, 7, 9}),
        'p_dorian': frozenset({0, 2, 5, 7, 10}),
        'p_phrygian': frozenset({0, 3, 5, 8, 10}),
        'p_mixolydian': frozenset({0, 2, 5, 7, 9}),
        'p_minor': frozenset({0, 3, 5, 7, 10}),
    },
    'sudu': {
        's_major': frozenset({0, 2, 4, 5, 7, 9}),
        's_dorian': frozenset({0, 2, 3, 5, 7, 10}),
        's_phrygian': frozenset({0, 1, 3, 5, 8, 10}),
        's_lydian': frozenset({0, 2, 4, 7, 9, 11}),
        's_mixolydian': frozenset({0, 2, 5, 7, 9, 10}),
        's_minor': frozenset({0, 3, 5, 7, 8, 10}),
    },

    # chords: all have inversion number suffix to distinguish from scales
    # triads
    'major': named_intervals_rotations(frozenset({0, 4, 7}), 'major'),
    'minor': named_intervals_rotations(frozenset({0, 3, 7}), 'minor'),
    'diminished': named_intervals_rotations(frozenset({0, 3, 6}), 'diminished'),
    # 7th
    'maj7': named_intervals_rotations(frozenset({0, 4, 7, 11}), 'maj7'),
    '7': named_intervals_rotations(frozenset({0, 4, 7, 10}), '7'),
    'min7': named_intervals_rotations(frozenset({0, 3, 7, 10}), 'min7'),
    'half-dim7': named_intervals_rotations(frozenset({0, 3, 6, 10}), 'half-dim7'),
    'dim7': named_intervals_rotations(frozenset({0, 3, 6, 9}), 'dim7'),
    # 6th
    '6': named_intervals_rotations(frozenset({0, 4, 7, 9}), '6'),
    'm6': named_intervals_rotations(frozenset({0, 3, 7, 9}), 'm6'),
    # other
    'aug': named_intervals_rotations(frozenset({0, 4, 8}), 'aug'),
    'sus2': named_intervals_rotations(frozenset({0, 2, 7}), 'sus2'),
    'sus4': named_intervals_rotations(frozenset({0, 5, 7}), 'sus4'),

}
name_to_intervals = functools.reduce(operator.or_, name_to_intervals_kind_grouped.values())
intervals_to_name = {v: k for k, v in name_to_intervals.items()}
name_to_intervals_key = {kind: frozenset(kv.values()) for kind, kv in name_to_intervals_kind_grouped.items()}
intervals_key_to_name = {v: k for k, v in name_to_intervals_key.items()}

scale_order = {}
kinds = {}
for kind, kv in name_to_intervals_kind_grouped.items():
    scale_order[kind] = tuple(kv.keys())
    kinds.update(dict.fromkeys(kv.keys(), kind))

# colors
WHITE_PALE = Color.from_hex(0xAAAAAA)
BLACK_PALE = Color.from_hex(0x505050)
WHITE_BRIGHT = Color.from_hex(0xFFFFFF)
BLACK_BRIGHT = Color.from_hex(0x000000)
RED = Color.from_hex(0xFF0000)
GREEN = Color.from_hex(0x00FF00)
BLUE = Color.from_hex(0x4f88ea)


interval_colors = {
    0: Color(0xFF0000),
    1: Color.from_hex(0xFFB014),
    2: Color.from_hex(0xEFE600),
    3: Color.from_hex(0x00D300),
    4: Color.from_hex(0x4800FF),
    5: Color.from_hex(0xB800E5),
    6: Color.from_hex(0xFF00CB),
    7: Color.from_hex(0xFF0000),
    8: Color.from_hex(0xFFB014),
    9: Color.from_hex(0xEFE600),
    10: Color.from_hex(0x00D300),
    11: Color.from_hex(0x4800FF),
    12: Color.from_hex(0xB800E5),
    13: Color.from_hex(0xFF00CB),
}

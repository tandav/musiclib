import collections
import functools
import operator

from colortool import Color

from musiclib.util.etc import named_intervals_rotations

chromatic_notes = 'CdDeEFfGaAbB'
circle_of_fifths_clockwise = 'CGDAEBfdaebF'


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
    'pentatonic': {
        'p_major': frozenset({0, 2, 4, 7, 9}),
        'p_dorian': frozenset({0, 2, 5, 7, 10}),
        'p_phrygian': frozenset({0, 3, 5, 8, 10}),
        'p_mixolydian': frozenset({0, 2, 5, 7, 9}),
        'p_minor': frozenset({0, 3, 5, 7, 10}),
    },
    'h_minor': named_intervals_rotations(frozenset({0, 2, 3, 5, 7, 8, 11}), 'h_minor'),
    'h_major': named_intervals_rotations(frozenset({0, 2, 4, 5, 7, 8, 11}), 'h_major'),
    'm_minor': named_intervals_rotations(frozenset({0, 2, 3, 5, 7, 9, 11}), 'm_minor'),
    # chords: all have inversion number suffix to distinguish from scales
    # triads
    'major': named_intervals_rotations(frozenset({0, 4, 7}), 'major'),
    'minor': named_intervals_rotations(frozenset({0, 3, 7}), 'minor'),
    'dim': named_intervals_rotations(frozenset({0, 3, 6}), 'dim'),
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
_intervals_to_names = collections.defaultdict(set)
for n, i in name_to_intervals.items():
    _intervals_to_names[i].add(n)
intervals_to_names = {k: frozenset(v) for k, v in _intervals_to_names.items()}
name_to_intervals_key = {kind: frozenset(kv.values()) for kind, kv in name_to_intervals_kind_grouped.items()}
intervals_key_to_name = {v: k for k, v in name_to_intervals_key.items()}

scale_order = {}
kinds = {}
for kind, kv in name_to_intervals_kind_grouped.items():
    scale_order[kind] = tuple(kv.keys())
    kinds.update(dict.fromkeys(kv.keys(), kind))

nths = {
    'triads': frozenset({0, 2, 4}),
    'sixths': frozenset({0, 2, 4, 5}),
    'sevenths': frozenset({0, 2, 4, 6}),
    'ninths': frozenset({0, 2, 4, 6, 8}),
}

# colors
WHITE_PALE = Color(0xAAAAAA)
BLACK_PALE = Color(0x505050)
WHITE_BRIGHT = Color(0xFFFFFF)
BLACK_BRIGHT = Color(0x000000)
RED = Color(0xFF0000)
GREEN = Color(0x00FF00)
BLUE = Color(0x4F88EA)


interval_colors = {
    0: Color(0xFF0000),
    1: Color(0x8B4513),
    2: Color(0xFF7F00),
    3: Color(0xFFFF00),
    4: Color(0x00FF00),
    5: Color(0x228B22),
    6: Color(0x8FBC8F),
    7: Color(0x00FFFF),
    8: Color(0x1E90FF),
    9: Color(0x0000FF),
    10: Color(0x8C00FC),
    11: Color(0xFF00FF),
}

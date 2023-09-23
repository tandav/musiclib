import itertools
from musiclib.util.etc import intervals_rotations


# todo: delete this and move to util/names.py
scale_order = {
    'natural': ('major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'),
    'pentatonic': ('p_major', 'p_dorian', 'p_phrygian', 'p_mixolydian', 'p_minor'),
    'harmonic': ('h_minor', 'h_locrian', 'h_major', 'h_dorian', 'h_phrygian', 'h_lydian', 'h_mixolydian'),
    'melodic': ('m_minor', 'm_locrian', 'm_major', 'm_dorian', 'm_phrygian', 'm_lydian', 'm_mixolydian'),
    'sudu': ('s_major', 's_dorian', 's_phrygian', 's_lydian', 's_mixolydian', 's_minor'),
    'c_major': ('c_major', 'c_major_inv1', 'c_major_inv2'),
    'c_minor': ('c_minor', 'c_minor_inv1', 'c_minor_inv2'),
}

# todo: inversions for all chords must be here
# c_major = 

kinds = (
    {k: 'natural' for k in scale_order['natural']} |
    {k: 'harmonic' for k in scale_order['harmonic']} |
    {k: 'melodic' for k in scale_order['melodic']} |
    {k: 'pentatonic' for k in scale_order['pentatonic']} |
    {k: 'sudu' for k in scale_order['sudu']} | 
    {k: 'c_major' for k in scale_order['c_major']} |
    {k: 'c_minor' for k in scale_order['c_minor']}
    # {
        # 'c_major': 'c_major',
        # 'c_minor': 'c_minor',
        # 'c_diminished': 'c_diminished',
        # 'c_maj7': 'c_maj7',
        # 'c_7': 'c_7',
        # 'c_min7': 'c_min7',
        # 'c_half-dim7': 'c_half-dim7',
        # 'c_dim7': 'c_dim7',
        # 'c_6': 'c_6',
        # 'c_m6': 'c_m6',
        # 'c_aug': 'c_aug',
        # 'c_sus2': 'c_sus2',
        # 'c_sus4': 'c_sus4',
    # }
)

# name_to_intervals_grouped = {
#     'natural': (

#     ),
# }

name_to_intervals = {
    # natural
    'major': frozenset({0, 2, 4, 5, 7, 9, 11}),
    'dorian': frozenset({0, 2, 3, 5, 7, 9, 10}),
    'phrygian': frozenset({0, 1, 3, 5, 7, 8, 10}),
    'lydian': frozenset({0, 2, 4, 6, 7, 9, 11}),
    'mixolydian': frozenset({0, 2, 4, 5, 7, 9, 10}),
    'minor': frozenset({0, 2, 3, 5, 7, 8, 10}),
    'locrian': frozenset({0, 1, 3, 5, 6, 8, 10}),
    # harmonic
    'h_minor': frozenset({0, 2, 3, 5, 7, 8, 11}),
    'h_locrian': frozenset({0, 1, 3, 5, 6, 9, 10}),
    'h_major': frozenset({0, 2, 4, 5, 8, 9, 11}),
    'h_dorian': frozenset({0, 2, 3, 6, 7, 9, 10}),
    'h_phrygian': frozenset({0, 1, 4, 5, 7, 8, 10}),
    'h_lydian': frozenset({0, 3, 4, 6, 7, 9, 11}),
    'h_mixolydian': frozenset({0, 1, 3, 4, 6, 8, 9}),
    # melodic
    'm_minor': frozenset({0, 2, 3, 5, 7, 9, 11}),
    'm_locrian': frozenset({0, 1, 3, 5, 7, 9, 10}),
    'm_major': frozenset({0, 2, 4, 6, 8, 9, 11}),
    'm_dorian': frozenset({0, 2, 4, 6, 7, 9, 10}),
    'm_phrygian': frozenset({0, 2, 4, 5, 7, 8, 10}),
    'm_lydian': frozenset({0, 2, 3, 5, 6, 8, 10}),
    'm_mixolydian': frozenset({0, 1, 3, 4, 6, 8, 10}),
    # pentatonic
    'p_major': frozenset({0, 2, 4, 7, 9}),
    'p_dorian': frozenset({0, 2, 5, 7, 10}),
    'p_phrygian': frozenset({0, 3, 5, 8, 10}),
    'p_mixolydian': frozenset({0, 2, 5, 7, 9}),
    'p_minor': frozenset({0, 3, 5, 7, 10}),
    # sudu
    's_major': frozenset({0, 2, 4, 5, 7, 9}),
    's_dorian': frozenset({0, 2, 3, 5, 7, 10}),
    's_phrygian': frozenset({0, 1, 3, 5, 8, 10}),
    's_lydian': frozenset({0, 2, 4, 7, 9, 11}),
    's_mixolydian': frozenset({0, 2, 5, 7, 9, 10}),
    's_minor': frozenset({0, 3, 5, 7, 8, 10}),

    # chords: all have c_ prefix to distinguish from scales
    # triads
    # major
    'c_major': frozenset({0, 4, 7}),
    'c_major_inv1': frozenset({0, 3, 8}),
    'c_major_inv2': frozenset({0, 5, 9}),
    # minor
    'c_minor': frozenset({0, 3, 7}),
    'c_minor_inv1': frozenset({0, 4, 9}),
    'c_minor_inv2': frozenset({0, 5, 8}),
    # diminished
    # 'c_diminished': frozenset({0, 3, 6}),
    # # 7th
    # 'c_maj7': frozenset({0, 4, 7, 11}),
    # 'c_7': frozenset({0, 4, 7, 10}),
    # 'c_min7': frozenset({0, 3, 7, 10}),
    # 'c_half-dim7': frozenset({0, 3, 6, 10}),
    # 'c_dim7': frozenset({0, 3, 6, 9}),
    # # 6th
    # 'c_6': frozenset({0, 4, 7, 9}),
    # 'c_m6': frozenset({0, 3, 7, 9}),
    # # etc
    # 'c_aug': frozenset({0, 4, 8}),
    # 'c_sus2': frozenset({0, 2, 7}),
    # 'c_sus4': frozenset({0, 5, 7}),
}

name_to_intervals_key = {
    'natural': frozenset({
        name_to_intervals['major'],
        name_to_intervals['dorian'],
        name_to_intervals['phrygian'],
        name_to_intervals['lydian'],
        name_to_intervals['mixolydian'],
        name_to_intervals['minor'],
        name_to_intervals['locrian'],
    }),
    'harmonic': frozenset({
        name_to_intervals['h_major'],
        name_to_intervals['h_dorian'],
        name_to_intervals['h_phrygian'],
        name_to_intervals['h_lydian'],
        name_to_intervals['h_mixolydian'],
        name_to_intervals['h_minor'],
        name_to_intervals['h_locrian'],
    }),
    'melodic': frozenset({
        name_to_intervals['m_major'],
        name_to_intervals['m_dorian'],
        name_to_intervals['m_phrygian'],
        name_to_intervals['m_lydian'],
        name_to_intervals['m_mixolydian'],
        name_to_intervals['m_minor'],
        name_to_intervals['m_locrian'],
    }),
    'pentatonic': frozenset({
        name_to_intervals['p_major'],
        name_to_intervals['p_dorian'],
        name_to_intervals['p_phrygian'],
        name_to_intervals['p_mixolydian'],
        name_to_intervals['p_minor'],
    }),
    'sudu': frozenset({
        name_to_intervals['s_major'],
        name_to_intervals['s_dorian'],
        name_to_intervals['s_phrygian'],
        name_to_intervals['s_lydian'],
        name_to_intervals['s_mixolydian'],
        name_to_intervals['s_minor'],
    }),
    # 'c_major': intervals_rotations(name_to_intervals['c_major']),
    'c_major': frozenset({
        name_to_intervals['c_major'],
        name_to_intervals['c_major_inv1'],
        name_to_intervals['c_major_inv2'],
    }),
    # 'c_minor': intervals_rotations(name_to_intervals['c_minor']),
    # 'c_diminished': intervals_rotations(name_to_intervals['c_diminished']),
    # 'c_maj7': intervals_rotations(name_to_intervals['c_maj7']),
    # 'c_7': intervals_rotations(name_to_intervals['c_7']),
    # 'c_min7': intervals_rotations(name_to_intervals['c_min7']),
    # 'c_half-dim7': intervals_rotations(name_to_intervals['c_half-dim7']),
    # 'c_dim7': intervals_rotations(name_to_intervals['c_dim7']),
    # 'c_6': intervals_rotations(name_to_intervals['c_6']),
    # 'c_m6': intervals_rotations(name_to_intervals['c_m6']),
    # 'c_aug': intervals_rotations(name_to_intervals['c_aug']),
    # 'c_sus2': intervals_rotations(name_to_intervals['c_sus2']),
    # 'c_sus4': intervals_rotations(name_to_intervals['c_sus4']),
}

from colortool import Color

chromatic_notes = 'CdDeEFfGaAbB'  # TODO make variable here, delete from config, reimport everywhere, maybe circular imports
note_i = {note: i for i, note in enumerate(chromatic_notes)}


neighsbors_min_shared = {'natural': 0, 'pentatonic': 0}

natural = 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'
pentatonic = 'p_major', 'p_dorian', 'p_phrygian', 'p_mixolydian', 'p_minor'
harmonic = 'h_minor', 'h_locrian', 'h_major', 'h_dorian', 'h_phrygian', 'h_lydian', 'h_mixolydian'
melodic = 'm_minor', 'm_locrian', 'm_major', 'm_dorian', 'm_phrygian', 'm_lydian', 'm_mixolydian'
sudu = 's_major', 's_dorian', 's_phrygian', 's_lydian', 's_mixolydian', 's_minor'
kinds = (
    {k: 'natural' for k in natural} |
    {k: 'harmonic' for k in harmonic} |
    {k: 'melodic' for k in melodic} |
    {k: 'pentatonic' for k in pentatonic} |
    {k: 'sudu' for k in sudu}
)

WHITE_PALE = Color.from_hex(0xAAAAAA)
BLACK_PALE = Color.from_hex(0x505050)
WHITE_BRIGHT = Color.from_hex(0xFFFFFF)
BLACK_BRIGHT = Color.from_hex(0x000000)
RED = Color.from_hex(0xFF0000)
GREEN = Color.from_hex(0x00FF00)
BLUE = Color.from_hex(0x4f88ea)

scale_colors = {
    'major': Color(0xFF0000),
    'dorian': Color.from_hex(0xFFB014),
    'phrygian': Color.from_hex(0xEFE600),
    'lydian': Color.from_hex(0x00D300),
    'mixolydian': Color.from_hex(0x4800FF),
    'minor': Color.from_hex(0xB800E5),
    'locrian': Color.from_hex(0xFF00CB),
}

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

scale_colors['h_major'] = scale_colors['major']
scale_colors['h_dorian'] = scale_colors['dorian']
scale_colors['h_phrygian'] = scale_colors['phrygian']
scale_colors['h_lydian'] = scale_colors['lydian']
scale_colors['h_mixolydian'] = scale_colors['mixolydian']
scale_colors['h_minor'] = scale_colors['minor']
scale_colors['h_locrian'] = scale_colors['locrian']

scale_colors['m_major'] = scale_colors['major']
scale_colors['m_dorian'] = scale_colors['dorian']
scale_colors['m_phrygian'] = scale_colors['phrygian']
scale_colors['m_lydian'] = scale_colors['lydian']
scale_colors['m_mixolydian'] = scale_colors['mixolydian']
scale_colors['m_minor'] = scale_colors['minor']
scale_colors['m_locrian'] = scale_colors['locrian']

scale_colors['p_major'] = scale_colors['major']
scale_colors['p_dorian'] = scale_colors['dorian']
scale_colors['p_phrygian'] = scale_colors['phrygian']
scale_colors['p_mixolydian'] = scale_colors['mixolydian']
scale_colors['p_minor'] = scale_colors['minor']

scale_colors['s_major'] = scale_colors['major']
scale_colors['s_dorian'] = scale_colors['dorian']
scale_colors['s_phrygian'] = scale_colors['phrygian']
scale_colors['s_lydian'] = scale_colors['lydian']
scale_colors['s_mixolydian'] = scale_colors['mixolydian']
scale_colors['s_minor'] = scale_colors['minor']


chord_colors = {
    'minor': scale_colors['minor'],
    'major': scale_colors['major'],
    'diminished': scale_colors['locrian'],
}

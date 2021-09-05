
from . import util

midi = True
midi_device = 'IAC Driver Bus 1'

chromatic_notes = 'CdDeEFfGaAbB'  # todo make variable here, delete from config, reimport everywhere, maybe circular imports
note_i = {note: i for i, note in enumerate(chromatic_notes)}


neighsbors_min_shared = {'diatonic': 0, 'pentatonic': 0}


diatonic = 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'
pentatonic = 'p_major', 'p_dorian', 'p_phrygian', 'p_mixolydian', 'p_minor'
kinds = {k: 'diatonic' for k in diatonic} | {k: 'pentatonic' for k in pentatonic}


# if change: also change in static/main.css
scale_colors = dict(
    major        = 'FFFFFF',
    dorian       = '54E346',
    phrygian     = '00FFCC',
    lydian       = '68A6FC',
    mixolydian   = 'FFF47D',
    minor        = 'D83A56',
    locrian      = 'B980F0',
    p_major      = 'FFFFFF',
    p_dorian     = '54E346',
    p_phrygian   = '00FFCC',
    p_mixolydian = 'FFF47D',
    p_minor      = 'D83A56',
)

WHITE_COLOR = (0xaa,) * 3
BLACK_COLOR = (0x50,) * 3
RED_COLOR = 0xff, 0, 0
GREEN_COLOR = 0, 0xff, 0
BLUE_COLOR = 0, 0, 0xff

chord_colors = {
    'minor': util.hex_to_rgb(scale_colors['minor']),
    'major': util.hex_to_rgb(scale_colors['major']),
    'diminished': util.hex_to_rgb(scale_colors['locrian']),
}

default_octave = 5

# piano_img_size = 14 * 60, 280
piano_img_size = 14 * 18, 85

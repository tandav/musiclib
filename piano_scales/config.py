from . import util

# chromatic_notes = 'SrRgGMmPdDnN'
chromatic_notes = 'CdDeEFfGaAbB'
# neighsbors_min_shared = {'diatonic': 5, 'pentatonic':3}
neighsbors_min_shared = {'diatonic': 0, 'pentatonic':0}


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

WHITE_COLOR = (170,) * 3
BLACK_COLOR = (80,) * 3
RED_COLOR = 255, 0, 0
GREEN_COLOR = 0, 255, 0
BLUE_COLOR = 0, 0, 255

chord_colors = {
    'minor': util.hex_to_rgb(scale_colors['minor']),
    'major': util.hex_to_rgb(scale_colors['major']),
    'diminished': util.hex_to_rgb(scale_colors['locrian']),
}

default_octave = 5

# piano_img_size = 14 * 60, 280
piano_img_size = 14 * 18, 85
import mido

device = 'IAC Driver Bus 1'
port = mido.open_output(device)

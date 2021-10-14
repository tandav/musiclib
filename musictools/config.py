chromatic_notes = 'CdDeEFfGaAbB'  # todo make variable here, delete from config, reimport everywhere, maybe circular imports
note_i = {note: i for i, note in enumerate(chromatic_notes)}


neighsbors_min_shared = {'diatonic': 0, 'pentatonic': 0}


diatonic = 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'
pentatonic = 'p_major', 'p_dorian', 'p_phrygian', 'p_mixolydian', 'p_minor'
sudu = 's_major', 's_dorian', 's_phrygian', 's_lydian', 's_mixolydian', 's_minor'
kinds = {k: 'diatonic' for k in diatonic} | {k: 'pentatonic' for k in pentatonic} | {k: 'sudu' for k in sudu}


# if change: also change in static/main.css
scale_colors = dict(
    major='FFFFFF',
    dorian='54E346',
    phrygian='00FFCC',
    lydian='68A6FC',
    mixolydian='FFF47D',
    minor='D83A56',
    locrian='B980F0',
)
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

WHITE_COLOR = (0xaa,) * 3
BLACK_COLOR = (0x50,) * 3
RED_COLOR = 0xff, 0, 0
GREEN_COLOR = 0, 0xff, 0
BLUE_COLOR = 0, 0, 0xff

chord_colors = {
    'minor': scale_colors['minor'],
    'major': scale_colors['major'],
    'diminished': scale_colors['locrian'],
}

default_octave = 5

# piano_img_size = 14 * 60, 280
piano_img_size = 14 * 18, 85
beats_per_minute = 120


# daw
sample_rate = 44100  # samples per second
# midi_file = 'static/midi/weird.mid'
# midi_file = 'static/midi/overlap.mid'
# midi_file = 'static/midi/dots.mid'
# midi_file = 'static/midi/halfbar.mid'
# midi_file = 'static/midi/halfbar-and-short.mid'
# midi_file = 'static/midi/4-16.mid'
midi_file = 'static/midi/3-4.mid'
chunk_size = 1024
chunk_seconds = chunk_size / sample_rate

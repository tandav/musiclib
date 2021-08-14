# chromatic_notes = 'SrRgGMmPdDnN'
chromatic_notes = 'CdDeEFfGaAbB'
neighsbors_min_shared = {'diatonic': 5, 'pentatonic':3}


bits_2_name = {
    '101011010101': 'major',
    '101101010110': 'dorian',
    '110101011010': 'phrygian',
    '101010110101': 'lydian',
    '101011010110': 'mixolydian',
    '101101011010': 'minor',
    '110101101010': 'locrian',

    '101010010100': 'p_major',
    '101001010010': 'p_dorian',
    '100101001010': 'p_phrygian',
    '101001010100': 'p_mixolydian',
    '100101010010': 'p_minor',
}

name_2_bits = {v: k for k, v in bits_2_name.items()}

diatonic = 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'
pentatonic = 'p_major', 'p_dorian', 'p_phrygian', 'p_mixolydian', 'p_minor'
kinds = {}
for k in diatonic: kinds[k] = 'diatonic'
for k in pentatonic: kinds[k] = 'pentatonic'

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

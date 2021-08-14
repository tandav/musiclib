# chromatic_notes = 'SrRgGMmPdDnN'
chromatic_notes = 'CdDeEFfGaAbB'
neighsbors_min_intersect = 5


# if change: also change in static/main.css
scale_colors = dict(
    major      = 'FFFFFF',
    dorian     = '54E346',
    phrygian   = '00FFCC',
    lydian     = '0F52BA',
    mixolydian = 'FFF47D',
    minor      = 'D83A56',
    locrian    = 'B980F0',
    diminished = 'B980F0',
)

bits_2_name = {
    '101011010101': 'major',
    '101101010110': 'dorian',
    '110101011010': 'phrygian',
    '101010110101': 'lydian',
    '101011010110': 'mixolydian',
    '101101011010': 'minor',
    '110101101010': 'locrian',
}
name_2_bits = {v: k for k, v in bits_2_name.items()}
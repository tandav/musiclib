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
midi_folder = 'static/midi/'
# midi_file = 'weird.mid'
# midi_file = 'overlap.mid'
# midi_file = 'dots.mid'
# midi_file = 'halfbar.mid'
# midi_file = 'halfbar-and-short.mid'
# midi_file = 'bassline.mid'
midi_file = 'drumloop.mid'
# midi_file = '4-4-8.mid'
# chunk_size = 1024 * 4
chunk_size = 1024
chunk_seconds = chunk_size / sample_rate
wav_output_file = 'out.wav'

# samples
kick = 'static/samples/kick-909.wav'
hat = 'static/samples/open-hat-909.wav'
clap = 'static/samples/clap-909.wav'


# streaming
audio_pipe = 'audio.fifo'
video_pipe = 'video.fifo'
fps = 30
# fps = 20
# fps = 60

frame_width = 426
frame_height = 240

# video_queue_item_size = 20
video_queue_item_size = 1
assert video_queue_item_size < fps


# OUTPUT_VIDEO = '/tmp/output.mp4'
# OUTPUT_VIDEO = '/dev/null'
OUTPUT_VIDEO = 'rtmp://a.rtmp.youtube.com/live2/u0x7-vxkq-6ym4-s4qk-0acg'

log_path = 'logs/log.jsonl'
